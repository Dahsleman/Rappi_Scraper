from __future__ import print_function
from algorithms.aditional_queries_algorithm import AditionalQueriesAlgorithm as AQA
from google_sheet.google_sheet_api import GoogleSheetApi
from utils.file_generator import FileGenerator
from fuzzy.prod.fuzzy_unitary import Fuzzy
from utils.rappi_utils import StringUtils
from input_settings import InputSettings
from node_code import NodeCode
from datetime import datetime
import subprocess
import geocoder 
import requests
import sys
import csv

def result():
  authorization = subprocess.run(['node', '-e', NodeCode.CODE], capture_output=True, text=True)
  return authorization

def getStoreAddress(bearer_token, store_id):
    url = f'https://services.rappi.com.br/api/web-gateway/web/stores-router/id/{store_id}/'

    request_heathers = {
        'authorization' : bearer_token,
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36' 
    }

    try:
        response = requests.get(url, headers=request_heathers)
        response.raise_for_status()
        if response.status_code == 200:
            json_data = response.json()
            store_address = json_data['address']
            return store_address

    except requests.exceptions.HTTPError as err:
        if response.status_code == 401:
            print('ERROR: NEED UPDATE TOKEN!!')
            exit()
        else:
            print('Request failed with status code, TRY AGAIN:', response.status_code)
            exit()
    except requests.exceptions.RequestException as err:
        print(f"REQUESTS ERROR, TRY AGAIN: {err}")
        exit()         

def storesList(lat, lng, query, bearer_token):
    stores_list = []
    # URL of the target endpoint
    url = 'https://services.rappi.com.br/api/pns-global-search-api/v1/unified-search?is_prime=false&unlimited_shipping=false'
    payload = {
        'lat': lat,
        'lng': lng,
        'options': {},
        'query': query,     
    }
    request_heathers = {
        'authorization' : bearer_token,
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36' 
    }
    
    try:
        response = requests.post(url, json=payload, headers=request_heathers)
        response.raise_for_status()
        if response.status_code == 200:
            json_data = response.json()
            stores = json_data['stores']
            stores_list = []
            for store in stores:
                store_dict = {}
                search_term = query
                store_id = store['store_id']
                store_address = getStoreAddress(bearer_token, store_id)
                store_name = StringUtils.getStoreName(store)
                products_list = StringUtils.getStoreProdcuts(store, store_id, store_address, store_name, search_term)
                store_dict[store_name] = products_list
                stores_list.append(store_dict)
            
            return stores_list
        else:
            print('Request failed with status code, TRY AGAIN:', response.status_code)
            exit()
    
    except requests.exceptions.HTTPError as err:
        if response.status_code == 401:
            print('ERROR: NEED UPDATE TOKEN!!')
            exit()
        else:
            print('Request failed with status code, TRY AGAIN:', response.status_code)
            exit()
    except requests.exceptions.RequestException as err:
        print(f"REQUESTS ERROR, TRY AGAIN: {err}")
        exit()     

def geoAddress(address:str)->dict:
    g = geocoder.bing(address, key='Avs2Cjo6niYkuxjLApix0m6tplpt9qfz0SIgrW3_qoqGPZk62AsQCAxlraCz1oyV')
    results = g.json
    return results

def getStoreProducts(_querys, _bearer_token, _search_dict):
    if len(_querys) != 0:
        for query, keyword in _querys.items():
            if keyword != "":
                term = query[0]
                unit = query[1]
                unit = unit.lower()
                if unit != "" and (unit == "kg" or unit == "gr" or unit == "l" or unit == "ml" or unit == "und"):
                    stores_list = storesList(results['lat'], results['lng'], term, _bearer_token)
                    query_list = list(query)
                    query_list[1] = unit
                    query = tuple(query_list)
                    print(term)
                    _search_dict[(query,keyword)] = stores_list
                    return _search_dict
                else:
                    print(f'QUERY:{term}:{unit}')
                    print(f'Type diferent unit for {term}')
                    exit()
            else:
                print(f'Insert a keyword for: {query}')
                exit()       
    else:
        print('Input querys')
        exit()

def getFirstQuery(_querys):
    querys_dict = {}
    first_query = list(_querys.items())[0]
    querys_dict[first_query[0]] = first_query[1]
    return querys_dict

"""INPUTS"""
original_queries_dic = {}
clientDetails = InputSettings.CLIENTS[int(sys.argv[1])]
address = clientDetails["__ADDRESS__"]
client = clientDetails["__NAME__"]
querys = clientDetails["__QUERY__"]
query = getFirstQuery(querys)
AQA.addAditionalQueries(query, original_queries_dic)

"""PROGRAM"""
current_datetime = datetime.now()
formatted_time = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(f'START: {formatted_time}')

print(f'SELECTED CLIENT: {client}')

if len(address) != 0:
    results = geoAddress(address)
    print('Adress OK')
else:
    print('Input an address')
    exit()

current_datetime = datetime.now()
formatted_time = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(f'ADDRESS: {formatted_time}')

# Get the bearer_token
try:
    authorization = result()
    bearer_token = authorization.stdout.strip()
    print('Using generated Bearer_token')
except:
    if bearer_token:
        bearer_token
        print('Using default Bearer_token')
    else:
        print('Input bearer_token')
        exit()

current_datetime = datetime.now()
formatted_time = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(f'TOKEN: {formatted_time}')

search_dict = {}
search_dict = getStoreProducts(query, bearer_token, search_dict)

products_list = []
for stores in search_dict.values():
    for store in stores:
        for store_items in store.values():
            for items in store_items:
                products_list.append(items)

current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")

datetime_products_list = []
for product in products_list:
    items = list(product.items())
    items.insert(0, ('k collected-at', formatted_datetime))
    product = dict(items)
    datetime_products_list.append(product)

current_datetime = datetime.now()
formatted_time = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(f'SCRAPPER: {formatted_time}')

print(f'TOTAL PRODUCTS SCRAPED: {len(datetime_products_list)}')

if len(datetime_products_list) > 0:
    keys = datetime_products_list[0].keys()
    with open('./output.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(datetime_products_list)

if len(datetime_products_list) > 0:
    GoogleSheetApi.update_google_sheet(datetime_products_list, clientDetails)

current_datetime = datetime.now()
formatted_time = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(f'EXCEL: {formatted_time}')
