# Apify Setup Guide

This guide walks you through the setup of an Apify Actor to scrape Chrome extension reviews using Python and Playwright.

## Step-by-Step Setup

1. **Create an Apify Account**  
   - Go to [Apify.com](https://www.apify.com) and sign up for a new account or log in if you already have an account.

2. **Create a New Actor**  
   - Navigate to the [Apify Console](https://console.apify.com/actors/new).
   - Select the **Python + Playwright** template to ensure compatibility with the code provided.

3. **Upload the Required Files**  
   - Replace the template files with the following files in your actor:
     - `main.py`: The main script that handles the scraping process.
     - `input_schema.json`: Defines the input schema for the actor.
     - `actor.json`: Contains metadata about the actor configuration.
     - `requirements.txt`: Specifies the dependencies needed for the actor.

4. **Build the Actor**  
   - Once all files are uploaded, click on the **Build** button.
   - Wait for the build process to complete. You should see a success message once it’s done.

5. **Retrieve the API Token**  
   - After the build is successful, navigate to the **API** section of your actor.
   - Click on **API Client** to get your **API Token**. This token will allow you to programmatically trigger the actor and access its results.

6. **Next Steps**  
   - You can now use the API token to integrate your Apify Actor with other applications, triggering the actor as needed to scrape and fetch data.

---

## File Descriptions

- **main.py**: The main Python script containing the logic for scraping Chrome extension reviews.
- **input_schema.json**: Defines the structure of inputs that your actor will accept.
- **actor.json**: Configuration file that provides metadata for the actor.
- **requirements.txt**: Lists the Python dependencies required by the actor, such as `playwright`.

---

## Example API Usage

With your **API Token** in hand, you can trigger the actor via API for automated scraping. Refer to Apify’s [API documentation](https://docs.apify.com) for more details on how to interact with your actor programmatically.

---

This setup will enable you to create a functional Apify Actor to scrape Chrome extension reviews and access it via API!
