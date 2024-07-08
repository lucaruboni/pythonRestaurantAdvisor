from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import firebase_admin
from firebase_admin import credentials, firestore
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta, timezone
import json
import os
from dotenv import load_dotenv
import random
import string

load_dotenv()  # Load environment variables from .env file

app = FastAPI()

# Load restaurant data from JSON
with open('restaurants.json', 'r') as file:
    restaurants = json.load(file)

# Load country data from JSON
with open('countries.json', 'r') as file:
    countries = json.load(file)

# Convert list of countries to a dictionary for easier access
countries_dict = {country["code"]: country for country in countries}

# Firebase setup
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Twilio setup
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
client = Client(twilio_account_sid, twilio_auth_token)

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.start()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

def generate_unique_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.get("/form/{restaurant_id}", response_class=HTMLResponse)
async def get_form(request: Request, restaurant_id: str):
    if restaurant_id not in restaurants:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    restaurant = restaurants[restaurant_id]
    return templates.TemplateResponse("form.html", {
        "request": request,
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant["name"],
        "bg_image": f"/static/img/{restaurant['bg_image']}",
        "logo": f"/static/img/{restaurant['logo']}",
        "countries": countries
    })

@app.post("/submit", response_class=JSONResponse)
async def submit_form(
    restaurant_id: str = Form(...), 
    name: str = Form(...), 
    email: str = Form(...), 
    phone: int = Form(...), 
    country: str = Form(...), 
    privacyPolicy: bool = Form(...)
):
    errors = {}
    if restaurant_id not in restaurants:
        errors["restaurant_id"] = "Restaurant not found"
    if not privacyPolicy:
        errors["privacyPolicy"] = "You must agree to the privacy policy and cookies."

    # Verify that the phone number contains only digits
    if not str(phone).isdigit():
        errors["phone"] = "Phone number must contain only digits."

    # Check if the phone number is already used
    existing_entries = db.collection(restaurant_id).where("phone", "==", phone).stream()
    if any(existing_entries):
        errors["phone"] = "This phone number has already been used."

    if errors:
        return JSONResponse(content={"detail": errors}, status_code=400)

    # Generate unique code
    unique_code = generate_unique_code()

    data = {
        'name': name,
        'email': email,
        'phone': phone,  # Save phone as integer
        'country': country,
        'timestamp': datetime.now(tz=timezone.utc).isoformat(),
        'code': unique_code,
        'validated': False
    }
    db.collection(restaurant_id).add(data)

    # Personalized message with validation code
    validation_message = f"Hi {name}, 🚀 Thank you for your feedback! Your unique code is: {unique_code}. Please validate it to receive your offer."
    send_whatsapp_message(countries_dict[country]['code'] + str(phone), validation_message)

    # Schedule promotional messages
    promotional_message = f"Hi {name}, 🚀 Enjoy a unique offer: Buy One Get One Free! 🤑"
    initial_schedule_time = datetime.now(tz=timezone.utc) + timedelta(minutes=1)
    schedule_promotional_messages(restaurant_id, countries_dict[country]['code'] + str(phone), name, initial_schedule_time)

    return JSONResponse(content={"detail": "Form submitted successfully", "restaurant_id": restaurant_id}, status_code=200)

@app.get("/thankyou", response_class=HTMLResponse)
async def thank_you(request: Request, restaurant_id: str):
    if restaurant_id not in restaurants:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    restaurant = restaurants[restaurant_id]
    return templates.TemplateResponse("thankyou.html", {
        "request": request,
        "bg_image": f"/static/img/{restaurant['bg_image']}",
        "logo": f"/static/img/{restaurant['logo']}",
        "message": "Please check your WhatsApp for the validation code.",
        "restaurant_id": restaurant_id
    })

@app.post("/validate", response_class=JSONResponse)
async def validate_code(
    restaurant_id: str = Form(...), 
    code: str = Form(...)
):
    if restaurant_id not in restaurants:
        return JSONResponse(content={"detail": "Restaurant not found"}, status_code=404)
    
    # Verify the code
    entries = db.collection(restaurant_id).where("code", "==", code).stream()
    valid_entry = None
    for entry in entries:
        valid_entry = entry
        break
    
    if not valid_entry:
        return JSONResponse(content={"detail": "Invalid code"}, status_code=400)
    
    # Check if the code is already validated
    entry_data = valid_entry.to_dict()
    if entry_data.get("validated", False):
        return JSONResponse(content={"detail": "Code already used"}, status_code=400)

    # Mark as validated
    db.collection(restaurant_id).document(valid_entry.id).update({"validated": True})

    return JSONResponse(content={"detail": "Code validated successfully"}, status_code=200)

@app.get("/validate/{restaurant_id}", response_class=HTMLResponse)
async def validate_form(request: Request, restaurant_id: str):
    if restaurant_id not in restaurants:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    restaurant = restaurants[restaurant_id]
    return templates.TemplateResponse("validate.html", {
        "request": request,
        "restaurant_id": restaurant_id,
        "bg_image": f"/static/img/{restaurant['bg_image']}",
        "logo": f"/static/img/{restaurant['logo']}"
    })

def send_whatsapp_message(phone_number, message):
    try:
        client.messages.create(
            body=message,
            from_=f"whatsapp:{twilio_whatsapp_number}",
            to=f"whatsapp:{phone_number}"
        )
    except Exception as e:
        print(f"Failed to send WhatsApp message to {phone_number}: {e}")

def schedule_message(restaurant_id, message, phone_number, schedule_time):
    scheduler.add_job(
        send_scheduled_message,
        trigger=DateTrigger(run_date=schedule_time),
        args=[restaurant_id, message, phone_number],
        misfire_grace_time=3600  # Allow up to 1 hour for missed jobs to run
    )

def schedule_promotional_messages(restaurant_id, phone_number, name, initial_schedule_time):
    message = f"Hi {name}, 🚀 Thank you for your feedback! Enjoy a unique offer: Buy One Get One Free! 🤑"
    follow_up_time = initial_schedule_time
    for i in range(5):  # Schedule 5 follow-up messages
        schedule_message(restaurant_id, message, phone_number, follow_up_time)
        follow_up_time += timedelta(minutes=1)

def send_scheduled_message(restaurant_id, message, phone_number):
    try:
        client.messages.create(
            body=message,
            from_=f"whatsapp:{twilio_whatsapp_number}",
            to=f"whatsapp:{phone_number}"
        )
    except Exception as e:
        print(f"Failed to send WhatsApp message to {phone_number} for {restaurant_id}: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
