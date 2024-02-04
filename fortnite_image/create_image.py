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

api = fortnite_api.FortniteAPI('9ffab28b-c928-4dfe-a43b-26d3b3b5ce58')
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

        date_obj = datetime.fromisoformat(date_str.rstrip('Z'))
        date = date_obj.strftime('%Y-%m-%d')

        data_to_save = current_shop.raw_data['featured']['entries']

        json_data = json.dumps(current_shop.raw_data, indent=4)

        # Print to a JSON file
        with open('featured_items.json', 'w') as file:
            file.write(json_data)

        print(GREEN + "Data saved to featured_items.json")

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

            if data['bundle']:
                image = data['bundle']['image']
                name = data['bundle']['name']
            else:
                image = data['items'][0]['images']['featured']
                name = data['devName'].split(',')[0].replace('[VIRTUAL]1 x', '')
                name = name.split(' for ')[0]
            joined_name = ''.join(name.split()).replace("'", "")
            
            item_history = len(data['items'][0]['shopHistory'])
            if item_history == 1:
                new_items += 1
            
            if not image:
                total_items -= 1
                continue

            html_content_div += f"""
            <div id={joined_name}>
                <img src={image} alt="product" />
                <P>{name}<br /> <span class="price"><span><img class="v-bucks-logo" src="{current_shop.raw_data['vbuckIcon']}" alt="">{price}</span> <span>{item_history} Days</span></span></p>
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
            <span>{date}</span>
            <span>Shop Items {total_items} ({new_items} New Items)</span>
        </h1>

        <section>
            {html_content_div}
        </section>
        <section id='footer'>hipdiscovery</section>
        </body>
        </html>
        """

        css_content += """
        body {
        background-color: black;
        color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 100vh;
        }
        #footer {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 5px;
        padding-bottom: 5px;
        color: white;
        font-size: 20px;
        font-style: italic;
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
        --tw-space-x-reverse: 0;
        margin-right: calc(1rem/* 5px */ * var(--tw-space-x-reverse));
        margin-left: calc(1rem/* 5px */ * calc(1 - var(--tw-space-x-reverse)));
        }
        h1 {
        font-size: 15px;
        display: flex;
        flex-direction: column;
        align-items: center;
        }
        span {
        line-height: 13px;
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

get_screenshot()