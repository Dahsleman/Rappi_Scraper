import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import geocoder 
import subprocess
import asyncio

# Define the Node.js code as a string
node_code = """
const puppeteer = require('puppeteer');
async function scrapeNetworkDevTools() {
  // Launch a headless Chrome browser
  const browser = await puppeteer.launch();
  // Create a new page
  const page = await browser.newPage();
  // Enable request interception
  await page.setRequestInterception(true);
  // Create an array to store intercepted requests
  const interceptedRequests = [];
  // Listen for request events
  page.on('request', (request) => {
    interceptedRequests.push(request);
    request.continue();
  });
  // Navigate to the desired URL
  await page.goto('https://www.rappi.com.br/');
  // Perform other interactions or wait for the page to load as needed
  // Print the intercepted requests
  for (const request of interceptedRequests) {
    if (request.url() == 'https://services.rappi.com.br/api/pns-global-search-api/v1/unified-recent-top-searches' && request.method() == 'POST' ) {
        const headersJson = JSON.stringify(request.headers(), null, 2);
        const headers = JSON.parse(headersJson);
        const authorization = headers.authorization;
        console.log(authorization);
    }
  }
  // Close the browser
  await browser.close();
}
// Run the scraping function
scrapeNetworkDevTools();
"""

# Execute the Node.js code as a subprocess
async def result():
    authorization = subprocess.run(['node', '-e', node_code], capture_output=True, text=True)
    return authorization


def update_xlsx_file(filename, address):
    # Create a new dataframe with the address
    df = pd.DataFrame({'Address': [address]})

    # Write the dataframe to the Excel file
    with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='Address', index=False)
        print(f"{xlsx_file} updated.")


def create_xlsx(json_file, xlsx_file, sheet_name):
    # Read the JSON file into a dataframe
    df = pd.read_json(json_file)
    
    # Create a new Excel file
    try:
        with pd.ExcelWriter(xlsx_file) as writer:
            # Write the dataframe to the Excel sheet
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"{xlsx_file} created.")
            return True
    except:
        print(f'ERROR: please close {xlsx_file} and run again')
        return False


def storesDict(lat, lng, query, bearer_token):
    stores_dict = {}
    # URL of the target endpoint
    url = 'https://services.rappi.com.br/api/pns-global-search-api/v1/unified-search?is_prime=false&unlimited_shipping=false'
    payload = {
    'lat': lat,
    'lng': lng,
    'query': query, 
    'options': {}
    }
    bearer_token = bearer_token
    request_heathers = {
    'authorization' : bearer_token,
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36' 
    }
    
    response = requests.post(url, json=payload, headers=request_heathers)
    
    if response.status_code == 200:
        json_data = response.json()
        stores = json_data['stores']
        for store in stores:
            store_name = store['store_name']
            store_id = store['store_id']
            store_type = store['store_type']
            store_type = store_type.replace("_","-")
            store_path = f"{store_id}-{store_type}"
            stores_dict[store_name] = store_path
        return stores_dict
    elif response.status_code == 401:
        print('NEED ANOTHER TOKEN:')
        return stores_dict
    else:
        print('Request failed with status code:', response.status_code)
        return stores_dict

def geoAddress(address:str)->dict:
    g = geocoder.bing(address, key='Avs2Cjo6niYkuxjLApix0m6tplpt9qfz0SIgrW3_qoqGPZk62AsQCAxlraCz1oyV')
    results = g.json
    return results

"""INPUTS"""

"bearer_token"
bearer_token = "Bearer ft.gAAAAABknia5hDruuYatY6X3ACVSQNqsoBoiEHAem2Yz_uHEiRCbTS1gYGRM8Rf-WS65UL8mU4NdwczK047mdf47TXcyyjKHs-wAwdfYc_Gc_2fEcYoYuHEDUY9vsnshXLjXSsa9XQuaD3sl1k7hkkrffRbwjM8gL8uV-secx9dULv7RL6MyAW2oO6LnOOFWKxtNQKCS8dR1whDplGoVNOCZKBIVHrKL_av0JBRlmSGgHqyC4JFKYCt_wtoJ2TyR9TrYnyCdbbKe9VFDr3GyNPa_kMMIO5bxUkTAqyYvXWudXeE4m9TOTJQI-gzFqjoa1IfPNBC27qmgM7EytTSG9dr1VT2choC0k2kFVDX16i6QPwGxuR1d5rE="

"Colocar o endereco igual no google maps"
address = 'R. Jandiatuba, 74 - Buritis, Belo Horizonte - MG, 30493-135'

"""
Colocar as querys dentro da lista igual exemplo.
Exemplo:

querys = [
    'desodorante',
    'sabao em po',
]
"""
querys = [
    # 'desodorante',
    # 'sabao em po',
    # 'cafe',
    # 'manteiga',
]

client = 'Kompru_teste_search'

"""PROGRAM"""

current_datetime = datetime.now()
formatted_time = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(f'START SCRAPING: {formatted_time}')

# # Get the bearer_token
# authorization = asyncio.run(result())
# bearer_token = authorization.stdout.strip()

if len(address) != 0:
    results = geoAddress(address)
else:
    print('Input an address')
    exit()

lat = results['lat']
lng = results['lng']

stores_query = {}
if len(querys) != 0:
    for query in querys:
        stores_dict = storesDict(lat, lng, query, bearer_token)
        stores_query[query] = stores_dict
else:
    print('Input querys')
    exit()

# Create json_file of products.
jsonFile = f'Rappi_{client}'
with open(f'{jsonFile}.json', 'w') as fp:
    json.dump(stores_query, fp, indent=4)

# Create xlsx file
json_file = f'{jsonFile}.json'
xlsx_file = f'Rappi_{client}_allStores_Query.xlsx'
sheet_name = 'Stores'
bolean = create_xlsx(json_file, xlsx_file, sheet_name)

if bolean == True:
    update_xlsx_file(xlsx_file, address)

current_datetime = datetime.now()
formatted_time = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(f'END SCRAPING: {formatted_time}')



