import json
import requests
import time
import re
import csv
from datetime import datetime

def search(string:str)->dict:
    string_dict = {}
    """find sub_aisle"""
    start_index = string.rfind("/") + 1  # Find the index of the last '/'
    end_index = string.rfind(".json")  # Find the index of '.json'

    if start_index != -1 and end_index != -1:
        sub_aisle = string[start_index:end_index]
        string_dict['sub_aisle'] = sub_aisle 
    else:
        return print("Subaisle not found in the string.")

    """find aisle"""
    pattern = rf"/([a-zA-Z]+)/{sub_aisle}.json"
    match = re.search(pattern, string)

    if match:
        aisle = match.group(1)
        string_dict['aisle'] = aisle
    else:
        return print("Aisle not found in the string.")

    """find store"""
    pattern = rf"/([^/]+)/{aisle}"
    match = re.search(pattern, string)

    if match:
        store = match.group(1)
        string_dict['store'] = store
    else:
        return print("Store not found in the string.")
    
    return string_dict

def sub_aisleScraper(url:str, referer:str, sub_aisle:str, aisle:str, store:str)->list:
    products_list = []
    request_heather = {'referer':f'{referer}'}
    response = requests.get(url, headers=request_heather)

    if response.status_code == 429:
        print('TOO MANY PRODUCTS REQUESTS: WAIT 30s')
        time.sleep(30)
        response = requests.get(url, headers=request_heather)
        json_data = response.json()
    elif response.status_code == 502:
        print('BAD GATEWAY: WAIT 1m')
        response = requests.get(url, headers=request_heather)
        json_data = response.json()
    else:
        json_data = response.json()

    pageProps = json_data['pageProps']
    fallback = pageProps['fallback']
    storefront = fallback[f'storefront/{store}/{aisle}/{sub_aisle}']
    aisle_detail_response = storefront['aisle_detail_response']
    data = aisle_detail_response['data']
    components = data['components']

    for component in components:
        resource = component['resource']
        products = resource['products']
        for product in products:
            products_list.append(product)

    #add datetime 
    new_products_list = []
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")
    for product in products_list:
        items = list(product.items())
        items.insert(0, ('collected_at', formatted_datetime))
        product = dict(items)
        new_products_list.append(product)

    return new_products_list

"""EXAMPLE OF URL AND REFERER"""    
# url = 'https://www.rappi.com.br/_next/data/OQW5XdLHt3Z3a5AIQ4kxd/pt-BR/ssg/900027422-verdemar/hortifruti/frutas.json'
# referer = 'https://www.rappi.com.br/lojas/900027422-verdemar/hortifruti/frutas'
url = input('Request URL:')
referer = input('Referer:')

url_dict = search(url)
sub_aisle = url_dict['sub_aisle']
aisle = url_dict['aisle']
store = url_dict['store']

products_list = sub_aisleScraper(url, referer, sub_aisle, aisle, store)
print(f'TOTAL PRODUCTS SCRAPED: {len(products_list)}')

# Create json_file.
jsonFile = f'Rappi_{store}_{aisle}_{sub_aisle}'
with open(f'{jsonFile}.json', 'w') as fp:
    json.dump(products_list, fp, indent=4)

json_file_path = f'{jsonFile}.json'
# Read the JSON file
with open(json_file_path, "r") as json_file:
    json_data = json.load(json_file)

# Extract the headers from the first JSON object
headers = list(json_data[0].keys())

csv_file_path = f'Rappi_{store}_{aisle}_{sub_aisle}.csv'
# Write the JSON data to a CSV file
with open(csv_file_path, "w", encoding="utf-8", newline="") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=headers)

    # Write the header row
    writer.writeheader()

    # Write the data rows
    writer.writerows(json_data)

print("CSV file created.")
