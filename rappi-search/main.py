import json
from datetime import datetime
import os
from utils.utils import (result, update_xlsx_with_address, update_xlsx_with_json, create_xlsx_with_json, 
                        products_scraper, storesList, geoAddress)
from input.input import client, address, querys

search_dict = {}
new_products_list = []
datetime_products_list = []
new_error_list = []
datetime_error_list = []

if len(client) == 0:
    print('Input client')
    exit()

if len(address) != 0:
    results = geoAddress(address)
    print('Adress OK')
else:
    print('Input an address')
    exit()
    
lat = results['lat']
lng = results['lng']

# Get the bearer_token
authorization = result()
bearer_token = authorization.stdout.strip()

if bearer_token:
    if len(querys) != 0:
        for query, keyword in querys.items():
            if keyword != "":
                term = query[0]
                unit = query[1]
                unit = unit.lower()
                if unit != "" and (unit == "kg" or unit == "gr" or unit == "l" or unit == "ml" or unit == "und"):
                    stores_list = storesList(lat, lng, term, bearer_token)
                    query_list = list(query)
                    query_list[1] = unit
                    query = tuple(query_list)
                    search_dict[(query,keyword)] = stores_list
                else:
                    print(f'QUERY:{term}:{unit}')
                    print(f'Type diferent unit for {term}')
                    exit()
            else:
                print(f'Insert a keyword for: {query}')
                exit()       
        print('Querys OK')
    else:
        print('Input querys')
        exit()
else:
    print('ERROR to update bearer token')

current_datetime = datetime.now()
formatted_time = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(f'STARTING SCRAPING: {formatted_time}')

for querys, stores in search_dict.items():
    keywords = querys[1]
    query = querys[0]
    term = query[0]
    unit = query[1]
    print(f'SCRAPING {term} SEARCH PRODUCTS')
    if term.rfind(" ") != -1:
        term = term.replace(' ','%20')
    for store in stores:
        products_list, error_list = products_scraper(store, term, unit, keywords)
        for products in products_list:
            new_products_list.append(products)
        for error in error_list:
            if error['error'] != "":
                new_error_list.append(error)

#add datetime 
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")
for product in new_products_list:
    items = list(product.items())
    items.insert(0, ('k collected-at', formatted_datetime))
    product = dict(items)
    datetime_products_list.append(product)
    datetime_error_list.append(product)
print(f'TOTAL PRODUCTS SCRAPED: {len(datetime_products_list)}')

directory_path = "G:/My Drive/kompru/data"
directory_name = client

try:
    # os.mkdir(f'data/{directory_name}')
    os.mkdir(f'{directory_path}/{directory_name}')
    print(f'Directory {directory_name} created')
except FileExistsError:
    print(f'Directory {directory_name} already exist')

file_path_drive = f'{directory_path}/{directory_name}/{client}'
file_path_errors_drive = f'{directory_path}/{directory_name}/{client}_erros'

if os.path.isfile(f'{file_path_drive}.json'):
    with open(f'{file_path_drive}.json', 'r') as json_file:
        existing_data = json.load(json_file)
    for item in datetime_products_list:
        existing_data.append(item)
    with open(f'{file_path_drive}.json', 'w') as fp:
        json.dump(existing_data, fp, indent=4)
else:
    # Create json_file of products.
    with open(f'{file_path_drive}.json', 'w') as fp:
        json.dump(datetime_products_list, fp, indent=4)

if os.path.isfile(f'{file_path_errors_drive}.json'):
    with open(f'{file_path_errors_drive}.json', 'r') as json_file:
        existing_data = json.load(json_file)
    for item in new_error_list:
        existing_data.append(item)
    with open(f'{file_path_errors_drive}.json', 'w') as fp:
        json.dump(existing_data, fp, indent=4)
else:
    # Create json_file of errors.
    with open(f'{file_path_errors_drive}.json', 'w') as fp:
        json.dump(new_error_list, fp, indent=4)

current_datetime = datetime.now()
formatted_time = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(f'END SCRAPING: {formatted_time}')


xlsx_file = f'{file_path_drive}.xlsx'
jsonFile_products = f'{file_path_drive}.json'
jsonFile_errors = f'{file_path_errors_drive}.json'
sheet_products = 'Products'
sheet_errors = 'Erros'

create_xlsx_with_json(jsonFile_products, xlsx_file, sheet_products)
update_xlsx_with_json(jsonFile_errors, xlsx_file, sheet_errors)
update_xlsx_with_address(xlsx_file, address)


