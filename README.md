# Google Review Widget Scraper

The Google Review Widget Scraper project enables users to embed reviews of Chrome extensions directly on their website. By entering a Chrome extension URL, users can fetch reviews from the database or, if necessary, initiate a review scrape. The widget offers various customization options to fit seamlessly into any website design.

## Table of Contents

1. [Features](#features)
2. [Setup](#setup)
   - [Supabase Setup](#supabase-setup)
   - [Apify Actor Setup](#apify-actor-setup)
3. [Usage](#usage)
   - [Widget Customization](#widget-customization)
   - [Embedding the Widget](#embedding-the-widget)
4. [Project Workflow](#project-workflow)
5. [Contributing](#contributing)
6. [License](#license)

---

## Features

- **Embed Chrome Extension Reviews**: Easily display Chrome extension reviews on your website.
- **Extensive Customization**: Adjust widget colors, fonts, and dimensions to match website aesthetics.
- **Automatic Review Scraping**: If reviews are unavailable, the project triggers an Apify API to scrape the reviews within 5 minutes.
- **Real-time Preview**: Users can customize the widget with live previews.

---

## Setup

To set up the project, follow these steps:

### Supabase Setup

1. Create a Supabase project and set up the following tables:

   ```sql
   CREATE TABLE extension_info (
       id SERIAL PRIMARY KEY,
       extension_name TEXT UNIQUE NOT NULL,
       extension_url TEXT,
       developer TEXT,
       overall_rating float,
       total_rating integer,
       extension_type TEXT,
       total_users TEXT
   );

   CREATE TABLE extension_review (
       id SERIAL PRIMARY KEY,
       extension_name TEXT NOT NULL,
       name TEXT,
       date DATE,
       rating float,
       review TEXT,
       helpful TEXT
   );
   ```

2. Save the Supabase URL and API key, as these will be required to connect the project to the database.

### Apify Actor Setup

1. Create an Apify Actor to scrape Chrome extension reviews.  
2. Add the scraping code to your actor (link to the code can be added here once it’s available).
3. Save the Apify API key, as it will be needed to trigger the actor from the main application if reviews are not found in Supabase.

### Hosting on Vercel

1. Host the main project file on [Vercel.app](https://vercel.com/) for smooth and scalable deployment.
2. Ensure all environment variables (Supabase and Apify keys) are securely set up in the Vercel environment settings.

---

## Usage

### Widget Customization

1. **Enter Extension URL**: On the main website, enter the URL of the desired Chrome extension.
2. **Fetch Reviews**: Click the "Fetch Review" button. The system will first check the Supabase database:
   - If the URL is found, you’ll be directed to the widget customization page with a live preview.
   - If not found, the Apify API will initiate scraping, and you’ll receive a notification to check back in 5 minutes.
3. **Customize the Widget**: Modify the widget’s appearance using these options:
   - Outer background color
   - Card and rating colors
   - 20 different font styles
   - Adjustable widget height and width for perfect layout integration

### Embedding the Widget

1. After customizing, click the "Get Embed Code" button to generate a `<div>` block.
2. Copy and paste the embed code into your website to display the Chrome extension reviews.

---

## Project Workflow

1. **User Input**:
   - The user enters a Chrome extension URL in the input field.
   
2. **Database Check**:
   - The system checks if the extension URL is in the Supabase database.
   - If found, it routes to the customization page, showing a live preview of the widget.
   
3. **Review Scraping (if not found)**:
   - If no review data is found, an Apify API request initiates a scrape of the Chrome extension reviews.
   - A notification informs the user to wait for 5 minutes before refreshing to see the reviews.

4. **Widget Customization and Embedding**:
   - Users customize the widget's appearance and obtain an embed code to place it on their website.

---

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
