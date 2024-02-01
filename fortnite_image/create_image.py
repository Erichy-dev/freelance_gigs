from datetime import datetime
import fortnite_api
import json

api = fortnite_api.FortniteAPI('9ffab28b-c928-4dfe-a43b-26d3b3b5ce58')
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def get_daily_item_shop():
    try:
        current_shop = api.shop.fetch()
        
        date_str = current_shop.raw_data['date']
        date_obj = datetime.fromisoformat(date_str.rstrip('Z'))

        date = date_obj.strftime('%A, %B %d, %Y')

        data_to_save = current_shop.raw_data['featured']['entries']

        json_data = json.dumps(data_to_save, indent=4)

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
        <h1><span>Fortnite Item Shop</span><br /><span>{date}</span><br /><span>Shop Items {len(data_to_save)}</span></h1>

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
                <P>{name}<br /> <span class="price"><img class="v-bucks-logo" src="./v-bucks.jpg" alt="">{price}</span></p>
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
        width:30px;
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

get_daily_item_shop()