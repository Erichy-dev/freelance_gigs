from datetime import datetime
import fortnite_api
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

api = fortnite_api.FortniteAPI('9ffab28b-c928-4dfe-a43b-26d3b3b5ce58')
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def get_daily_item_shop():
    try:
        new_items = get_new_items()

        current_shop = api.shop.fetch()
        
        date_str = current_shop.raw_data['date']
        date_obj = datetime.fromisoformat(date_str.rstrip('Z'))

        date = date_obj.strftime('%A, %B %d, %Y')

        data_to_save = current_shop.raw_data['featured']['entries']

        json_data = json.dumps(current_shop.raw_data, indent=4)

        # Print to a JSON file
        with open('featured_items.json', 'w') as file:
            file.write(json_data)

        print(GREEN + "Data saved to featured_items.json")

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
        <h1><span>Fortnite Item Shop</span><br /><span>{date}</span><br /><span>Shop Items {len(data_to_save)} ({new_items} New Items)</span></h1>

        <section>
        """

        # Adding repeated div elements
        for data in data_to_save:
            price = data['finalPrice']

            if data['bundle']:
                image = data['bundle']['image']
                name = data['bundle']['name']
            else:
                image = data['items'][0]['images']['featured']
                name = data['devName'].split(',')[0].replace('[VIRTUAL]1 x', '')
                name = name.split(' for ')[0]
            
            if not image:
                continue
            html_content += f"""
            <div>
                <img src={image} alt="product" />
                <P>{name}<br /> <span class="price"><img class="v-bucks-logo" src="{current_shop.raw_data['vbuckIcon']}" alt="">{price}</span></p>
            </div>
            """

        # Closing section and body tags
        html_content += """
        </section>
        </body>
        </html>
        """

        # CSS content
        css_content = """
        body {
        background-color: black;
        color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        }

        section {
        display: grid;
        grid-template-columns: repeat(6, minmax(0, 1fr));
        width: 100%;
        }

        div {
        margin: 2px;
        }

        div, p {
        display: flex;
        flex-direction: column;
        align-items: center;
        }

        img {
        width: 99%;
        }
        .v-bucks-logo {
        width:20px;
        }
        .price {
        display: flex;
        flex-direction: row;
        align-items: center;
        }
        h1 {
        font-size: 15px;
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

def get_new_items():
    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'none'
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    driver.get('https://fortnite.gg/shop?game=br&different')

    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href="/shop?game=br&different"].filter.active',)))
    new_items = driver.find_element(By.CSS_SELECTOR, 'a[href="/shop?game=br&different"].filter.active > span').get_attribute('innerHTML')

    driver.execute_script("window.stop();")

    return new_items

get_daily_item_shop()