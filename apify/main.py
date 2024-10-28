from urllib.parse import urljoin
from playwright.async_api import async_playwright
from apify import Actor
from supabase import create_client, Client
from bs4 import BeautifulSoup
import re

# Supabase configuration
url = 'add your supabase url'
key = 'add your supabase key'
supabase: Client = create_client(url, key)

async def main() -> None:
    """
    The main coroutine is being executed using `asyncio.run()`, so do not attempt to make a normal function
    out of it, it will not work. Asynchronous execution is required for communication with Apify platform,
    and it also enhances performance in the field of web scraping significantly.
    """
    async with Actor:
        # Read the Actor input
        actor_input = await Actor.get_input() or {}
        link = actor_input.get('curl')
        ccurl= actor_input.get('curl')

        if not link:
            Actor.log.info('No URL specified in actor input, exiting...')
            await Actor.exit()

        # Ensure the link ends with '/reviews'
        if not link.endswith('/reviews'):
            link = f'{link.rstrip("/")}/reviews'

        # Launch Playwright and open a new browser context
        Actor.log.info('Launching Playwright...')
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=Actor.config.headless)
            page = await browser.new_page()

            # Load the page
            await page.goto(link)

            # Click "Load more" button and wait for content to load
            while True:
                try:
                    load_more_button = await page.query_selector('button:has-text("Load more")')
                    if load_more_button:
                        await load_more_button.click()
                        await page.wait_for_timeout(2000)  # Wait for 2 seconds to load more content
                    else:
                        break
                except Exception as e:
                    Actor.log.info(f"No more 'Load more' button found or an error occurred: {e}")
                    break

            # Get the updated page content
            html = await page.content()

            # Parse the page with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # Extract data using BeautifulSoup
            names = [item.get_text(strip=True) for item in soup.find_all(class_='LfYwpe')]
            dates = [item.get_text(strip=True) for item in soup.find_all(class_='ydlbEf')]
            ratings = [
                        float(re.search(r'(\d+(\.\d+)?)', item.get('aria-label', '').strip()).group(0))
                        if re.search(r'(\d+(\.\d+)?)', item.get('aria-label', '').strip())
                        else None
                        for item in soup.find_all(class_='B1UG8d')
                    ]
            reviews = [item.get_text(strip=True) for item in soup.find_all(class_='fzDEpf')]
            helpfuls = [item.get_text(strip=True) for item in soup.find_all(class_='ZRk0Tb')]

            extension_name_elements = soup.find_all(class_='Pa2dE')
            extension_url_elements = soup.find_all('a', class_='KgGEHd')
            developer_elements = soup.find_all(class_='cJI8ee')
            overall_rating_elements = soup.find_all(class_=['GlMWqe', 'SxpA2e'])
            overall_rating_elements = [re.search(r"\d+(\.\d+)?", element.get_text()).group() for element in overall_rating_elements if re.search(r"\d+(\.\d+)?", element.get_text())]
            total_rating_elements = soup.find_all(class_='PloaX')
            total_rating_elements = [re.search(r"\d+", element.get_text()).group() for element in total_rating_elements if re.search(r"\d+", element.get_text())]
            extension_type_elements = soup.find_all(class_=['gqpEIe', 'bgp7Ye'])
            total_users_elements = soup.find_all(class_='F9iKBc')

            extension_name = extension_name_elements[0].get_text(strip=True) if extension_name_elements else 'No name found'
            if extension_url_elements:
                href = extension_url_elements[0].get('href', '').strip()
                extension_url = 'https://chromewebstore.google.com' + href.lstrip('.') if href else 'No URL found'
            else:
                extension_url = 'No URL found'

            developer = developer_elements[0].get_text(strip=True) if developer_elements else 'No developer found'
            overall_rating = float(overall_rating_elements[0]) if overall_rating_elements else 'No rating found'
            total_rating = int(total_rating_elements[0]) if total_rating_elements else 'No total rating found'

            if total_users_elements:
                total_users_text = total_users_elements[0].get_text(strip=True)
                total_users_match = re.search(r'(\d+,\d+|\d+)', total_users_text)
                total_users = total_users_match.group(0) if total_users_match else 'No total users found'
            else:
                total_users = 'No total users found'

            if extension_type_elements:
                extension_type = extension_type_elements[-1].get_text(strip=True)
            else:
                extension_type = 'No type found'

            # Log extracted values
            Actor.log.info(f"Extension Name: {extension_name}")
            Actor.log.info(f"Extension URL: {extension_url}")
            Actor.log.info(f"Developer: {developer}")
            Actor.log.info(f"Overall Rating: {overall_rating}")
            Actor.log.info(f"Total Rating: {total_rating}")
            Actor.log.info(f"Extension Type: {extension_type}")
            Actor.log.info(f"Total Users: {total_users}")

            # Check if extension info already exists
            existing_info = supabase.table('extension_info').select('*').eq('extension_name', extension_name).execute()
            if not existing_info.data:
                # Insert data into extension_info table
                extension_info_data = {
                    'extension_name': extension_name,
                    'extension_url': ccurl,
                    'developer': developer,
                    'overall_rating': overall_rating,
                    'total_rating': total_rating,
                    'extension_type': extension_type,
                    'total_users': total_users
                }
                extension_info_response = supabase.table('extension_info').insert(extension_info_data).execute()
                Actor.log.info("Extension info has been successfully stored in Supabase.")
                Actor.log.info(extension_info_response)
            else:
                Actor.log.info("Extension info already exists in the database.")

            # Ensure all lists are the same length
            length = min(len(names), len(dates), len(ratings), len(reviews), len(helpfuls))

            # Trim lists to the same length
            names = names[:length]
            dates = dates[:length]
            ratings = ratings[:length]
            reviews = reviews[:length]
            helpfuls = helpfuls[:length]

            # Prepare data for extension_review table
            extension_review_data = [
                {
                    'name': names[i],
                    'date': dates[i],
                    'rating': ratings[i],
                    'review': reviews[i],
                    'helpful': helpfuls[i],
                    'extension_name': extension_name
                }
                for i in range(length)
            ]

            for review in extension_review_data:
                # Check if review already exists
                existing_review = supabase.table('extension_review').select('*').eq('name', review['name']).eq('date', review['date']).eq('rating', review['rating']).eq('review', review['review']).eq('helpful', review['helpful']).eq('extension_name', review['extension_name']).execute()
                if not existing_review.data:
                    # Insert data into extension_review table
                    extension_review_response = supabase.table('extension_review').insert(review).execute()
                    Actor.log.info("Review has been successfully stored in Supabase.")
                    Actor.log.info(extension_review_response)
                else:
                    Actor.log.info("Review already exists in the database.")

            # Clean up
            await browser.close()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
