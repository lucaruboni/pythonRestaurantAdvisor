# Restaurant Feedback Form with FastAPI

## Description
This project is a FastAPI application that allows customers to fill out a feedback form for a specific restaurant. After submitting the form, the customer receives a validation code via WhatsApp. The customer needs to present this code at the restaurant to activate a special promotion. The project uses Firebase Firestore for the database and Twilio for sending WhatsApp messages.

## Prerequisites
- [Anaconda](https://www.anaconda.com/products/individual) (Recommended for managing Python environments)
- Twilio account for sending WhatsApp messages
- Firebase credentials for Firestore

## Installation

### Step 1: Install Anaconda
- Download and install Anaconda following the official instructions [here](https://docs.anaconda.com/anaconda/install/).

### Step 2: Clone the Repository
- Clone this repository to your local machine:

    git clone https://github.com/your-username/restaurant-feedback-form.git
    cd restaurant-feedback-form

### Step 3: Create and Activate a Conda Environment
- Open the terminal or command prompt (Anaconda Prompt on Windows) and create a new environment with Python 3.8:

    conda create --name fastapi-env python=3.8

- Activate the environment:

    conda activate fastapi-env

### Step 4: Install Dependencies
- Install the dependencies listed in requirements.txt:

    pip install -r requirements.txt

## Configuration
### Step 1: Set Environment Variables

- Create a .env file in the root directory of the project and add the following environment variables:

    TWILIO_ACCOUNT_SID=your_twilio_account_sid
    TWILIO_AUTH_TOKEN=your_twilio_auth_token
    TWILIO_WHATSAPP_NUMBER=your_twilio_whatsapp_number
    EMAIL_USER=your_mailtrap_username
    EMAIL_PASSWORD=your_mailtrap_password
    SMTP_SERVER=smtp.mailtrap.io
    SMTP_PORT=587

### Step 2: Add Firebase Credentials
- Download your Firebase credentials from your Firebase Console project and save them as firebase_credentials.json in the root directory of the project.

### Step 3: Configure Images and JSON Files
- Ensure you have the restaurants.json and countries.json files in the root directory of the project and that they are correctly configured with restaurant data and international prefixes.

## Running the Project
### Step 1: Start the Application
- Start the FastAPI server using Uvicorn:

    uvicorn main:app --reload

### Step 2: Access the Application
- Open your browser and go to http://127.0.0.1:8000/form/{restaurant_id} replacing {restaurant_id} with the specific restaurant's ID.

## Application Workflow
- Fill out the Form: The customer fills out the feedback form on the /form/{restaurant_id} page.
- Receive Validation Code: The customer receives a validation code via WhatsApp.
- Validate the Code: The restaurateur validates the code on the /validate/{restaurant_id} page.
- Activate Promotion: Once the code is validated, the customer receives promotional messages via WhatsApp.

## Additional Notes
- Debugging and Logs
You can view logs and error messages in the terminal where the FastAPI server is running. Ensure you have access to these logs to troubleshoot any issues during development and execution.

## Configuration Changes
If you make changes to the configuration files, credentials, or environment variables, restart the FastAPI server to apply the changes.

## Prevent Uploading Sensitive Files to GitHub
### Step 1: Create a .gitignore File
- Add the following lines to a .gitignore file in the root directory to prevent the .env and firebase_credentials.json files from being uploaded to GitHub:

    .env
    firebase_credentials.json

### Step 2: Verify .gitignore
- Ensure the .gitignore file is in the root directory and that it contains the entries for .env and firebase_credentials.json.

## Contributing
If you wish to contribute to this project, feel free to fork the repository and submit a pull request with your changes.