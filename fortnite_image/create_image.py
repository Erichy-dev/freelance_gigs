from datetime import datetime
import fortnite_api
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from PIL import Image
from io import BytesIO

import os

api = fortnite_api.FortniteAPI('')

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def get_dominant_color(image_url):
    # Download the image from the URL
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    # Resize the image to 1x1 pixel
    img = img.resize((1, 1))

    # Get the color
    dominant_color = img.getpixel((0, 0))
    return dominant_color

dominant_color = ''
css_content = """"""

def get_daily_item_shop():
    try:
        new_items = 0

        current_shop = api.shop.fetch()
        
        date_str = current_shop.raw_data['date']

        date = format_date_with_superscript(date_str)

        data_to_save = current_shop.raw_data['featured']['entries']

        json_data = json.dumps(current_shop.raw_data, indent=4)

        # Print to a JSON file
        with open('featured_items.json', 'w') as file:
            file.write(json_data)

        print(GREEN + "Data saved to featured_items.json", RESET)

        total_items = len(data_to_save)

        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="sample.css">
        <title>Document</title>
        </head>
        <body>
        """
        html_content_div = """"""

        # Adding repeated div elements
        for data in data_to_save:
            price = data['finalPrice']
            bg = data['layout']['background']
            if bg:
                global dominant_color
                dominant_color = get_dominant_color(bg)
            else:
                dominant_color = '(77, 84, 85)'

            if data['bundle']:
                image = data['bundle']['image']
                name = data['bundle']['name']
            else:
                image = data['items'][0]['images']['featured']
                name = data['devName'].split(',')[0].replace('[VIRTUAL]1 x', '')
                name = name.split(' for ')[0]
            joined_name = ''.join(name.split()).replace("'", "")
            
            item_history = len(data['items'][0]['shopHistory']) - 1
            item_history_days = f'{item_history} Days'
            if item_history == 0:
                new_items += 1
                item_history_days = '(NEW)'
            if item_history == 1:
                item_history_days = f'{item_history} Day'

            if not image:
                total_items -= 1
                continue

            html_content_div += f"""
            <div id={joined_name}>
                <img src={image} alt="product" />
                <p class='description'>
                    <span class='name'>{name}</span>
                    <span class="price">
                        <span>
                            <img class="v-bucks-logo" src="{current_shop.raw_data['vbuckIcon']}" alt="">
                            {price}
                        </span>
                        <span>{item_history_days}</span>
                    </span>
                </p>
            </div>
            """
            global css_content
            css_content += f"""
            #{joined_name} {{
            background-color: rgb{dominant_color};
            }}
            """

        html_content += f"""
        <h1>
            <span>Fortnite Item Shop</span>
            {date}
            <span>Shop Items {total_items} ({new_items} New Items)</span>
        </h1>

        <section>
            {html_content_div}
        </section>
        <section id='footer'>
            <span>Creator Code:</span>
            <span>hipdiscovery</span>
        </section>
        </body>
        </html>
        """

        css_content += """
        .description {
        font-weight: bold;
        font-size: 9px;
        display: flex;
        flex-direction: column;
        width: 100%;
        align-items: center;
        }
        body {
        background-color: black;
        color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 100vh;
        }
        #footer {
        font-weight: bold;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 5px;
        color: white;
        font-size: 10px;
        }

        section {
        display: grid;
        grid-template-columns: repeat(14, minmax(0, 1fr));
        width: 100%;
        }

        div {
        margin: 2px;
        }

        div, p {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 10px;
        }

        img {
        width: 99%;
        }
        .v-bucks-logo {
        width: 10px;
        }
        .price {
        display: flex;
        flex-direction: row;
        align-items: center;
        width: 100%;
        justify-content: space-between;
        }
        h1 {
        font-size: 15px;
        display: flex;
        flex-direction: column;
        align-items: center;
        }
        span {
        line-height: 20px;
        }
        """

        # Writing the HTML content to a file
        with open('sample.html', 'w') as file:
            file.write(html_content)

        # Writing the CSS content to a file
        with open('sample.css', 'w') as file:
            file.write(css_content)
        
        print(GREEN + 'done creating html file' + RESET)
        
    except Exception as e:
        print(RED + f"... An error occurred: {e} ...." + RESET)

def get_screenshot():
    get_daily_item_shop()

    driver = webdriver.Chrome()

    
    driver.get(f'file:///{os.getcwd()}/sample.html')
    driver.fullscreen_window()
    driver.save_screenshot('screenshot.png')
    print(GREEN, 'screenshot created', RESET)

def format_date_with_superscript(date_str):
    # Parsing the string to datetime object
    date_obj = datetime.fromisoformat(date_str.rstrip('Z'))

    # Extracting formatted month, day, and year
    formatted_month = date_obj.strftime('%B')
    day = date_obj.day
    formatted_year = date_obj.strftime('%Y')

    # Determine the ordinal suffix and construct the date string
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd", "th"][day % 10 - 1]

    # Construct the HTML paragraph with the superscript for the suffix
    html_paragraph = f'<span>{formatted_month} {day}<sup>{suffix}</sup>, {formatted_year}</span>'
    return html_paragraph

get_screenshot()