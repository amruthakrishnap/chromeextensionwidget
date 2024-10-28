from flask import Flask, request, jsonify, render_template_string
from supabase import create_client, Client
from apify_client import ApifyClient
import time
import threading
from datetime import datetime
from flask import render_template



# Initialize the Flask app
app = Flask(__name__)

# Supabase credentials
SUPABASE_URL = "Your Supabase_URL"
SUPABASE_KEY = "Your Supabase Key"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Apify client initialization
client = ApifyClient("apify_api_zbyqu2dzD94VC6iwhDzZ4uuPmKtM3t25AjRP")

# Route for the root (/) to serve the HTML form
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fetch Reviews</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .container {
                background-color: #fff;
                padding: 2em;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                width: 100%;
                max-width: 400px;
                text-align: center;
            }
            input[type="text"] {
                width: 100%;
                padding: 0.75em;
                margin-bottom: 1em;
                border-radius: 5px;
                border: 1px solid #ddd;
                font-size: 1em;
            }
            button {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 0.75em 1.5em;
                border-radius: 5px;
                font-size: 1em;
                cursor: pointer;
            }
            button:hover {
                background-color: #0056b3;
            }
            .error {
                color: red;
            }
            .popup {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                visibility: hidden;
            }
            .popup-content {
                background-color: white;
                padding: 2em;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            .timer {
                font-size: 2em;
                color: #007bff;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Enter Extension URL</h1>
            <form id="fetchReviewsForm">
                <input type="text" id="extensionUrl" name="extensionUrl" placeholder="https://example.com" required>
                <button type="submit">Fetch Reviews</button>
            </form>
            <p class="error" id="errorMessage"></p>
        </div>

        <!-- Popup for Review Not Found -->
        <div class="popup" id="popup">
            <div class="popup-content">
                <h2>Review not found in Supabase</h2>
                <p>Please wait while we fetch reviews. The page will refresh in <span class="timer" id="timer">300</span> seconds.</p>
            </div>
        </div>

        <script>
            document.getElementById('fetchReviewsForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const extensionUrl = document.getElementById('extensionUrl').value;

                // Call the server to check if the reviews exist
                const response = await fetch('/check_reviews', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ extension_url: extensionUrl })
                });
                const result = await response.json();

                if (result.status === 'found') {
                    // Redirect to the widget page with widget_id
                    const widgetId = result.widget_id;
                    window.location.href = `/widget?widget_id=${widgetId}&url=${extensionUrl}`;
                } else {
                    // Show error and start fetching reviews
                    document.getElementById('errorMessage').innerText = result.message;

                    // Trigger Apify actor and show the popup
                    document.getElementById('popup').style.visibility = 'visible';

                    // Timer countdown from 300 seconds (5 minutes)
                    let timer = 300;
                    const interval = setInterval(() => {
                        timer--;
                        document.getElementById('timer').innerText = timer;

                        if (timer === 0) {
                            clearInterval(interval);
                            window.location.reload();  // Refresh the page after 5 minutes
                        }
                    }, 1000);

                    // Fetch reviews from Apify
                    fetch('/run_apify_actor', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ extension_url: extensionUrl })
                    });
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/run_apify_actor', methods=['POST'])
def run_apify_actor():
    extension_url = request.json.get('extension_url')

    # Initialize Apify client with your API token
    client = ApifyClient("apify_api_zbyqu2dzD94VC6iwhDzZ4uuPmKtM3t25AjRP")

    # Prepare input for the Apify actor
    run_input = {
        "curl": extension_url
    }

    # Run the actor and wait for it to finish
    run = client.actor("7SshY9hNcK1GA49RO").call(run_input=run_input)

    # Optionally, handle the actor result and save to Supabase
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        # You can save the fetched reviews to Supabase here
        print(item)

    return jsonify({'status': 'fetching_started'})


# Check if reviews exist for the given URL and return widget_id
@app.route('/check_reviews', methods=['POST'])
def check_reviews():
    extension_url = request.json.get('extension_url')

    # Query the database to check if reviews exist for the given URL
    extension_info_data = supabase.table('extension_info').select("*").ilike("extension_url", extension_url).execute()

    if extension_info_data.data:
        widget_id = extension_info_data.data[0]['extension_name'].replace(" ", "_").lower()  # Create widget_id from extension name
        return jsonify({'status': 'found', 'widget_id': widget_id})
    else:
        return jsonify({'status': 'not_found', 'message': 'Reviews not found for the given URL.'})


@app.route('/widget')
def widget_page():
    widget_id = request.args.get('widget_id')  # Get the widget_id from the URL
    extension_url = request.args.get('url')  # Get the extension URL from the URL

    # Serve the widget_file.html with the widget_id dynamically injected
    return render_template('widget_file.html', widget_id=widget_id)




@app.route('/widget.js')
def serve_widget():
    from datetime import datetime

    # Get the widget ID from the URL query parameters
    widget_id = request.args.get('id')
    extension_name = widget_id.replace("_", " ").title()

    # Customization options via URL parameters (with default values)
    outer_bg_color = request.args.get('outer_bg_color', 'rgba(255, 255, 255, 0.9)')  # Default: translucent white for outer background
    inner_bg_color = request.args.get('inner_bg_color', '#f9f9f9')  # Default: light gray for inner widgets
    text_color = request.args.get('text_color', '#333')  # Default: dark gray for font color
    font_style = request.args.get('font_style', 'Arial, sans-serif')  # Default: Arial font style
    button_color = request.args.get('button_color', '#ff6600')  # Default: orange for Review Us button
    arrow_color = request.args.get('arrow_color', 'black')  # Default: black for carousel arrows
    outer_height = request.args.get('outer_height', 'auto')  # Default: auto height for outer container
    outer_width = request.args.get('outer_width', '100%')  # Default: 80% width for outer container
    card_height = request.args.get('card_height', '300px')  # Default: 300px height for cards
    card_width = request.args.get('card_width', '220px')  # Default: 220px width for cards
    card_bg_color = request.args.get('card_bg_color', '#ffffff')  # Default: white for card background
    star_color = request.args.get('star_color', 'gold')  # Default: gold for star ratings

    # Query extension_info for overall rating and total reviews using case-insensitive search
    extension_info_data = supabase.table('extension_info').select("*").ilike("extension_name", extension_name).execute()

    # Query extension_review for individual reviews using case-insensitive search
    extension_reviews_data = supabase.table('extension_review').select("*").ilike("extension_name", extension_name).execute()

    if extension_info_data.data and extension_reviews_data.data:
        # Extract overall rating and total reviews
        overall_rating = extension_info_data.data[0]['overall_rating']
        total_reviews = extension_info_data.data[0]['total_rating']
        extension_url = extension_info_data.data[0]['extension_url']
        reviews = extension_reviews_data.data

        # Set the number of items per view for the carousel
        items_per_view = 5

        # Calculate the number of days since the review was posted
        for review in reviews:
            try:
                review_date = datetime.strptime(review['date'], '%Y-%m-%d')  # Ensure format is YYYY-MM-DD
                days_ago = (datetime.now() - review_date).days
                review['days_ago'] = days_ago
            except ValueError as e:
                print(f"Error parsing date for review {review['id']}: {e}")
                review['days_ago'] = 'N/A'

        return render_template_string("""
        document.addEventListener('DOMContentLoaded', function() {
            var widgetDiv = document.querySelector('[data-widget-id="{{ widget_id }}"]');
            if (widgetDiv) {
                widgetDiv.innerHTML = `
                <style>
                    /* Main Outer Layer */
                    .widget-container {
                        border-radius: 15px;
                        border: 2px solid #e0e0e0;
                        padding: 30px;
                        max-width: {{ outer_width }};
                        margin: 0 auto;
                        font-family: {{ font_style }};
                        background-color: {{ outer_bg_color }};  /* Dynamic outer background color */
                        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
                        position: relative;
                        overflow: hidden;
                        height: {{ outer_height }}; /* Dynamic height */
                        color: {{ text_color }};  /* Dynamic font color */
                    }

                    .widget-header {
                        text-align: center;
                        font-size: 26px;
                        font-weight: bold;
                        margin-bottom: 15px;
                    }

                    /* Second Widget (Google Rating Section) */
                    .google-widget {
                        background-color: {{ inner_bg_color }};
                        padding: 25px;
                        border-radius: 15px;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 35px;
                        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.05);
                        transition: transform 0.3s ease, box-shadow 0.3s ease;
                    }

                    /* Center Google Image and Rating Section */
                    .google-logo {
                        width: 50px;
                        height: auto;
                        margin-right: 10px;
                    }

                    .google-rating {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 20px;
                    }

                    .google-rating .rating-value {
                        font-size: 32px;
                        font-weight: bold;
                        margin-right: 10px;
                    }

                    .stars {
                        display: flex;
                        align-items: center;
                        font-size: 24px;
                        margin-right: 10px;
                    }

                    .star {
                        color: {{ star_color }};  /* Dynamic star color */
                        margin-right: 5px;
                    }

                    .total-reviews {
                        font-size: 16px;
                        color: gray;
                    }

                    /* Review Button */
                    .review-button {
                        background-color: {{ button_color }};  /* Dynamic button color */
                        color: white;
                        padding: 12px 25px;
                        border-radius: 25px;
                        font-size: 16px;
                        text-decoration: none;
                        font-weight: bold;
                        transition: background-color 0.3s ease, transform 0.3s ease;
                    }

                    .review-button:hover {
                        background-color: {{ button_color|replace("#", "#e5") }};  /* Lighter hover effect */
                        transform: scale(1.05);
                    }

                    /* Carousel */
                    .carousel {
                        display: flex;
                        overflow: hidden;
                        margin-top: 20px;
                        position: relative;
                    }

                    .carousel-inner {
                        display: flex;
                        gap: 20px;
                        transition: transform 0.5s ease-in-out;
                        width: 100%;
                        justify-content: space-between;
                    }

                    .carousel-item {
                        border: 1px solid #ddd;
                        border-radius: 15px;
                        padding: 30px;
                        background: {{ card_bg_color }};  /* Dynamic card background color */
                        width: {{ card_width }};
                        height: {{ card_height }};
                        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                        flex-shrink: 0;
                        text-align: center;
                        transition: transform 0.3s ease, box-shadow 0.3s ease;
                    }

                    .carousel-item:hover {
                        transform: translateY(-5px);
                        box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.15);
                    }

                    .profile-circle {
                        background-color: #f0f0f0;
                        color: #007bff;
                        width: 50px;
                        height: 50px;
                        border-radius: 50%;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        font-size: 22px;
                        font-weight: bold;
                        margin: 0 auto 10px auto;
                    }

                    .profile-name {
                        text-align: center;
                        font-weight: bold;
                        font-size: 18px;
                        margin-bottom: 5px;
                    }

                    /* Display rating under profile name */
                    .profile-rating {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        margin-bottom: 10px;
                    }

                    .profile-rating .stars {
                        margin-right: 5px;
                    }

                    .review-text {
                        font-size: 16px;
                        color: {{ text_color }};
                        text-align: center;
                        margin-bottom: 10px;
                        word-wrap: break-word;
                    }

                    .posted-date {
                        font-size: 14px;
                        color: gray;
                        text-align: center;
                    }

                    .read-more {
                        font-size: 16px;
                        color: #ff6600;
                        cursor: pointer;
                        text-decoration: none;
                        margin-top: 10px;
                        display: block;
                        transition: color 0.3s ease;
                    }

                    .read-more:hover {
                        color: #e55b00;
                    }

                    /* Carousel Controls */
                    .carousel-control-prev,
                    .carousel-control-next {
                        position: absolute;
                        top: 50%;
                        background-color: transparent;  /* Transparent background */
                        color: {{ arrow_color }};  /* Dynamic arrow color */
                        border: none;
                        padding: 10px;
                        border-radius: 50%;
                        cursor: pointer;
                        z-index: 1;
                    }

                    .carousel-control-prev {
                        left: 10px;
                    }

                    .carousel-control-next {
                        right: 10px;
                    }

                    /* Dots for pagination */
                    .carousel-dots {
                        text-align: center;
                        margin-top: 20px;
                    }

                    .dot {
                        height: 12px;
                        width: 12px;
                        margin: 0 5px;
                        background-color: #007bff;
                        border-radius: 50%;
                        display: inline-block;
                        cursor: pointer;
                        opacity: 0.5;
                    }

                    .dot.active {
                        opacity: 1;
                        background-color: #ff6600;
                    }

                    /* Modal Style */
                    .modal {
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(0, 0, 0, 0.5);
                        display: none;
                        justify-content: center;
                        align-items: center;
                    }

                    .modal-content {
                        background-color: white;
                        border-radius: 15px;
                        padding: 20px;
                        width: 400px;
                        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                    }

                    .modal-content .profile-circle {
                        background-color: #f0f0f0;
                        color: #007bff;
                        width: 50px;
                        height: 50px;
                        border-radius: 50%;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        font-size: 24px;
                        font-weight: bold;
                        margin: 0 auto 10px auto;
                    }

                    .modal-close {
                        background-color: #ff6600;
                        color: white;
                        padding: 10px;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        margin-top: 10px;
                        text-align: center;
                        display: block;
                        width: 100%;
                    }
                </style>

                <div class="widget-container">
                    <!-- Widget Header -->
                    <div class="widget-header">
                        What Our Customers Say
                    </div>

                    <!-- Second Widget: Google Rating Section -->
                    <div class="google-widget">
                        <div class="google-rating">
                            <img src="google.png" alt="Google Logo" class="google-logo">
                            <span class="rating-value">{{ overall_rating }}</span>
                            <div class="stars">
                                {% set full_stars = overall_rating|int %}
                                {% set decimal_part = overall_rating - full_stars %}
                                {% set half_star = decimal_part >= 0.5 %}
                                
                                <!-- Full Stars -->
                                {% for i in range(full_stars) %}
                                    <span class="star">&#9733;</span>  <!-- Filled star for each full star -->
                                {% endfor %}

                                <!-- Half Star -->
                                {% if half_star %}
                                    <span class="star" style="background: linear-gradient(90deg, {{ star_color }} 50%, lightgray 50%); display: inline-block; -webkit-background-clip: text; color: transparent;">&#9733;</span>
                                {% endif %}

                                <!-- Empty Stars -->
                                {% for i in range(5 - full_stars - (half_star|int)) %}
                                    <span class="star" style="color: lightgray;">&#9734;</span>  <!-- Empty star for each missing rating point -->
                                {% endfor %}
                            </div>
                            <div class="total-reviews">({{ total_reviews }} reviews)</div>
                        </div>
                        <!-- Review Us Button below the rating -->
                        <a href="{{ extension_url }}" target="_blank" class="review-button">Review us on Google</a>
                    </div>

                    <!-- Reviews Carousel Section -->
                    <div class="carousel">
                        <div class="carousel-inner">
                            {% for review in reviews %}
                                <div class="carousel-item">
                                    <div class="profile-circle">
                                        {{ review['name'].split()[0][0].upper() }}{{ review['name'].split()[1][0].upper() if review['name'].split()|length > 1 else review['name'].split()[0][0].upper() }}
                                    </div>
                                    <div class="profile-name">{{ review['name'] }}</div>

                                    <!-- Rating for each card -->
                                    <div class="profile-rating">
                                        <div class="stars">
                                            {% set full_stars = review['rating']|int %}
                                            {% set half_star = (review['rating'] - full_stars) >= 0.5 %}

                                            <!-- Full Stars -->
                                            {% for i in range(full_stars) %}
                                                <span class="star">&#9733;</span>
                                            {% endfor %}

                                            <!-- Half Star -->
                                            {% if half_star %}
                                                <span class="star">&#9734;</span>
                                            {% endif %}

                                            <!-- Empty Stars -->
                                            {% for i in range(5 - full_stars - (half_star|int)) %}
                                                <span class="star" style="color: lightgray;">&#9734;</span>
                                            {% endfor %}
                                        </div>
                                    </div>

                                    <!-- Review text -->
                                    <div class="review-text">{{ review['review'] | truncate(100) }}</div>

                                    <!-- Read More button -->
                                    {% if review['review']|length > 100 %}
                                        <a href="#" class="read-more" data-full-text="{{ review['review'] }}">Read More</a>
                                    {% endif %}

                                    <!-- Posted Date -->
                                    <div class="posted-date">Review {{ review['days_ago'] }} days ago on <a href="{{ extension_url }}" target="_blank" style="color: #ff6600;">Google</a></div>
                                </div>
                            {% endfor %}
                        </div>

                        <!-- Carousel Controls -->
                        <button class="carousel-control-next">&#10095;</button>
                        <button class="carousel-control-prev">&#10094;</button>

                        <!-- Pagination Dots -->
                        <div class="carousel-dots">
                            {% for i in range((reviews|length // items_per_view) + (1 if reviews|length % items_per_view > 0 else 0)) %}
                                <span class="dot" data-index="{{ i }}"></span>
                            {% endfor %}
                        </div>
                    </div>
                </div>

                <!-- Modal for Full Review -->
                <div id="review-modal" class="modal">
                    <div class="modal-content">
                        <div class="profile-circle" id="modal-profile"></div>
                        <div class="profile-name" id="modal-name"></div>
                        <div class="review-text" id="modal-full-review"></div>
                        <button class="modal-close" id="modal-close">Close</button>
                    </div>
                </div>

                `;

                var carouselInner = document.querySelector('.carousel-inner');
                var prevButton = document.querySelector('.carousel-control-prev');
                var nextButton = document.querySelector('.carousel-control-next');
                var dots = document.querySelectorAll('.dot');
                var scrollAmount = 0;
                var itemWidth = document.querySelector('.carousel-item').clientWidth;
                var itemsPerView = {{ items_per_view }};

                function updateDots() {
                    dots.forEach(function(dot, index) {
                        var position = Math.abs(scrollAmount / (itemWidth * itemsPerView));
                        dot.classList.toggle('active', index === position);
                    });
                }

                nextButton.addEventListener('click', function() {
                    if (scrollAmount > -(carouselInner.scrollWidth - itemWidth * itemsPerView)) {
                        scrollAmount -= itemWidth * itemsPerView;  // Move carousel left
                        carouselInner.style.transform = 'translateX(' + scrollAmount + 'px)';
                        updateDots();
                    }
                });

                prevButton.addEventListener('click', function() {
                    if (scrollAmount < 0) {
                        scrollAmount += itemWidth * itemsPerView;  // Move carousel right
                        carouselInner.style.transform = 'translateX(' + scrollAmount + 'px)';
                        updateDots();
                    }
                });

                // Auto-scroll every 10 seconds
                setInterval(function() {
                    if (scrollAmount > -(carouselInner.scrollWidth - itemWidth * itemsPerView)) {
                        scrollAmount -= itemWidth * itemsPerView;
                    } else {
                        scrollAmount = 0;
                    }
                    carouselInner.style.transform = 'translateX(' + scrollAmount + 'px)';
                    updateDots();
                }, 10000);

                dots.forEach(function(dot, index) {
                    dot.addEventListener('click', function() {
                        scrollAmount = -index * itemWidth * itemsPerView;
                        carouselInner.style.transform = 'translateX(' + scrollAmount + 'px)';
                        updateDots();
                    });
                });

                // Modal Popup Logic for Read More
                document.querySelectorAll('.read-more').forEach(function(button) {
                    button.addEventListener('click', function(event) {
                        event.preventDefault();
                        var modal = document.getElementById('review-modal');
                        var fullReviewText = this.getAttribute('data-full-text');
                        var profileCircle = this.closest('.carousel-item').querySelector('.profile-circle').textContent;
                        var profileName = this.closest('.carousel-item').querySelector('.profile-name').textContent;

                        // Update modal content
                        document.getElementById('modal-profile').textContent = profileCircle;
                        document.getElementById('modal-name').textContent = profileName;
                        document.getElementById('modal-full-review').textContent = fullReviewText;

                        modal.style.display = 'flex';
                    });
                });

                document.getElementById('modal-close').addEventListener('click', function() {
                    document.getElementById('review-modal').style.display = 'none';
                });

                window.addEventListener('click', function(event) {
                    var modal = document.getElementById('review-modal');
                    if (event.target === modal) {
                        modal.style.display = 'none';
                    }
                });
            } else {
                console.error("Targeting div NOT found for ID: {{ widget_id }}");
            }
        });
        """, widget_id=widget_id, overall_rating=overall_rating, total_reviews=total_reviews, reviews=reviews, extension_url=extension_url, items_per_view=items_per_view, 
        outer_bg_color=outer_bg_color, text_color=text_color, button_color=button_color, card_bg_color=card_bg_color, star_color=star_color,outer_width=outer_width,outer_height=outer_height,card_width=card_width,arrow_color=arrow_color,card_height=card_height,inner_bg_color=inner_bg_color,font_style=font_style)
    else:
        print(f"No data found for extension: {extension_name}")
        return "console.error('No data found for this extension.');"

if __name__ == '__main__':
    app.run(debug=True)
