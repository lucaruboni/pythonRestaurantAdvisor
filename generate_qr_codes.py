import json
import qrcode

def generate_qr_codes_from_json(file_path):
    with open(file_path, 'r') as file:
        restaurants = json.load(file)
        for restaurant_id, restaurant_data in restaurants.items():
            url = f"http://127.0.0.1:8000/form/{restaurant_id}"
            img = qrcode.make(url)
            img.save(f"qr_{restaurant_id}.png")
            # Optionally update the JSON with the QR code path
            restaurant_data['form_qr_code'] = f"qr_{restaurant_id}.png"
    # Save the updated JSON
    with open(file_path, 'w') as file:
        json.dump(restaurants, file, indent=4)

# Generate QR codes for restaurants in the JSON file
generate_qr_codes_from_json('restaurants.json')
