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
