import json
import requests
import time
import re
import csv
from datetime import datetime

def aisleURL(url:str, aisle:str)->str:
    """Create aisle URL"""
    start_index = url.rfind("h")  
    end_index = url.rfind(".json")  

    if start_index != -1 and end_index != -1:
        url = url[start_index:end_index]
        new_url = f'{url}/{aisle}.json'
    else:
        return print("Something went wrong")
    return new_url

def subAisleURL(url:str, aisle:str, sub_aisle:str)->str:
    """Create subAisle URL"""
    start_index = url.rfind("h")  
    end_index = url.rfind(".json")  

    if start_index != -1 and end_index != -1:
        url = url[start_index:end_index]
        new_url = f'{url}/{aisle}/{sub_aisle}.json'
    else:
        return print("Subaisle not found in the string.")
    return new_url

def storeId(url:str)->str:
    """find store_id from URL"""
    start_index = url.rfind("/") + 1  
    end_index = url.rfind(".json")  
    if start_index != -1 and end_index != -1:
        store_id = url[start_index:end_index]
    else:
        return print("storeId not found in the url.")
    return store_id

def aisles(url: str)->list:
    """return an aisles list of a given store"""
    store_id=storeId(url)
    aisles_list=[]
    request_heather = {'referer':f'https://www.rappi.com.br/lojas/{store_id}/catalogo'}
    response = requests.get(url, headers=request_heather)

    if response.status_code == 429:
        print('TOO MANY PRODUCTS REQUESTS: WAIT 1m')
        time.sleep(60)
        print('REQUESTS STARTED')
        response = requests.get(url, headers=request_heather)
        json_data = response.json()
    else:
        json_data = response.json()

    pageProps = json_data['pageProps']
    fallback = pageProps['fallback']
    storefront = fallback[f'storefront/{store_id}']
    aisles_tree_response = storefront['aisles_tree_response']
    data = aisles_tree_response['data']
    components = data['components']

    for component in components:
        resource = component['resource']
        aisle = resource['friendly_url']
        if aisle != 'ofertas' and aisle != 'combos-e-packs' and aisle != 'outros':
            aisles_list.append(str(aisle))
    return aisles_list

def subAisles(url:str, aisle:str)->list:
    """return a subAisles list of a given store aisle"""
    sub_aisles_list=[]
    store_id=storeId(url)
    sub_aisle_url=aisleURL(url, aisle)
    request_heather = {'referer':f'https://www.rappi.com.br/lojas/{store_id}/catalogo'}
    response = requests.get(sub_aisle_url, headers=request_heather)

    if response.status_code == 429:
        print('TOO MANY PRODUCTS REQUESTS: WAIT 1m')
        time.sleep(60)
        print('REQUESTS STARTED')
        response = requests.get(sub_aisle_url, headers=request_heather)
        json_data = response.json()
    else:
        json_data = response.json()

    pageProps = json_data['pageProps']
    fallback = pageProps['fallback']
    storefront = fallback[f'storefront/{store_id}/{aisle}']
    sub_aisles_response = storefront['sub_aisles_response']
    data = sub_aisles_response['data']
    components = data['components']
    for component in components:
        resource = component['resource']
        sub_aisle = resource['friendly_url']
        sub_aisles_list.append(sub_aisle)
    
    return  sub_aisles_list

"""EXAMPLE OF URL"""
# url = f"https://www.rappi.com.br/_next/data/OQW5XdLHt3Z3a5AIQ4kxd/pt-BR/ssg/900027422-verdemar.json"
url = input('Request URL:')

#Create list of all store aisles
aisles_list = aisles(url)

#Create a dict of all subAisles of store aisles
aisles_dict = {}
for aisle in aisles_list:
    aisles_dict[aisle] = subAisles(url,aisle)

#Products scraper
products_list = []
store_id = storeId(url)
print(f'STARTING TO SCRAPE {store_id} PRODUCTS')
for key in aisles_dict:
    aisle = key
    subAisles_list = aisles_dict[key]
    subAisle_heather = subAisles_list[0]
    request_heather = {'referer':f'https://www.rappi.com.br/lojas/{store_id}/{aisle}/{subAisle_heather}'}
    for subAisle in subAisles_list:
        sub_aisle_url = subAisleURL(url,aisle,subAisle)
        response = requests.get(sub_aisle_url, headers=request_heather)
        if response.status_code == 429:
            print('TOO MANY REQUESTS: WAIT 1m')
            time.sleep(60)
            print('REQUESTS STARTED')
            response = requests.get(sub_aisle_url, headers=request_heather)
            json_data = response.json()
        elif response.status_code == 502:
            print('BAD GATEWAY: WAIT 2m')
            time.sleep(120)
            print('REQUESTS STARTED')
            response = requests.get(sub_aisle_url, headers=request_heather)
            json_data = response.json()
        else:
            json_data = response.json()

        pageProps = json_data['pageProps']
        fallback = pageProps['fallback']
        storefront = fallback[f'storefront/{store_id}/{aisle}/{subAisle}']
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
            #add formatted_datetime in the beginning of the list
            items = list(product.items())
            items.insert(0, ('collected_at', formatted_datetime))
            product = dict(items)
            new_products_list.append(product)

    print(f'{aisle} PRODUCTS SCRAPED:{len(new_products_list)}')
        
print(f'TOTAL PRODUCTS:{len(new_products_list)}')

# Create json_file.
jsonFile = f'Rappi_{store_id}'
with open(f'{jsonFile}.json', 'w') as fp:
    json.dump(new_products_list, fp, indent=4)
print("JSON file created!") 

# Read the JSON file
json_file_path = f'{jsonFile}.json'
with open(json_file_path, "r") as json_file:
    json_data = json.load(json_file)

# Extract the headers from the first JSON object
headers = list(json_data[0].keys())

# Write the JSON data to a CSV file
csv_file_path = f'Rappi_{store_id}.csv'
with open(csv_file_path, "w", encoding="utf-8", newline="") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=headers)

    # Write the header row
    writer.writeheader()

    # Write the data rows
    writer.writerows(json_data)

print("CSV file created!") 





