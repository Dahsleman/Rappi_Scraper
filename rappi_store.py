import json
import requests
import time
import re
import csv
from datetime import datetime
import socket
from bs4 import BeautifulSoup

def storeId(url:str)->str:
    """find store_id from URL"""
    string = url.replace(f"/catalogo", ".")
    start_index = string.rfind("/") + 1  
    end_index = string.rfind(".")  
    if start_index != -1 and end_index != -1:
        store_id = string[start_index:end_index]
    else:
        return print("storeId not found in the url.")
    
    return store_id

def buildId(url):
    urls = []
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("script")
        for link in links:
            string=link.get("src")
            if string is not None:
                urls.append(string)
        for url in urls:
            if url.rfind("_buildManifest.js") != -1:
                string = url.replace(f"/_buildManifest.js", ".js")
                start_index = string.rfind("/") + 1 
                end_index = string.rfind(".js")
                if start_index != -1 and end_index != -1:
                    bulid_id = string[start_index:end_index]
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    return bulid_id

def check_internet_connection():
    if socket.create_connection(("www.google.com", 80)):
        response = 200
    else:
        response = 500
    return response

def aisleURL(url:str, aisle:str)->str:
    """Create aisle URL"""
    string = url.replace(".json", "")  
    aisle_url = f'{string}/{aisle}.json'
    return aisle_url

def subAisleURL(url:str, aisle:str, sub_aisle:str)->str:
    """Create subAisle URL"""
    string = url.replace(".json", "")
    subAisle_url = f'{string}/{aisle}/{sub_aisle}.json'
    return subAisle_url

# def storeId(url:str)->str:
#     """find store_id from URL"""
#     start_index = url.rfind("/") + 1  
#     end_index = url.rfind(".json")  
#     if start_index != -1 and end_index != -1:
#         store_id = url[start_index:end_index]
#     else:
#         return print("storeId not found in the url.")
#     return store_id

def aisles(url:str, store_id:str)->list:
    """return an aisles list of a given store"""
    aisles_list=[]
    request_heather = {'referer':f'https://www.rappi.com.br/lojas/{store_id}/catalogo'}
    # status = check_internet_connection()
    # time.sleep(5)
    # while status != 200:
    #     print("No internet connection. Press enter to restart the program when conection is available")
    #     input()
    #     status = check_internet_connection()
    # if status == 200:
    #     print('INTERNET OK, STARTING REQUESTS')
    response = requests.get(url, headers=request_heather)
    if response.status_code == 429:
        print('TOO MANY REQUESTS: WAIT 1m')
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
        # if aisle != 'ofertas' and aisle != 'combos-e-packs' and aisle != 'outros':
        #     aisles_list.append(str(aisle))
        aisles_list.append(aisle)
    return aisles_list

def subAisles(url:str, aisle:str, store_id:str)->list:
    """return a subAisles list of a given store aisle"""
    sub_aisles_list=[]
    aisle_url=aisleURL(url, aisle)
    request_heather = {'referer':f'https://www.rappi.com.br/lojas/{store_id}/catalogo'}
    # status = check_internet_connection()
    # time.sleep(5)
    # while status != 200:
    #     print("No internet connection. Press enter to restart the program when conection is available")
    #     input()
    #     status = check_internet_connection()
    # if status == 200:
    response = requests.get(aisle_url, headers=request_heather)
    if response.status_code == 429:
        print('TOO MANY REQUESTS: WAIT 1m')
        time.sleep(60)
        print('REQUESTS STARTED')
        response = requests.get(aisle_url, headers=request_heather)
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
# url = "https://www.rappi.com.br/lojas/900155885-supermercado-dia/catalogo"
url = input('Request URL:')
store_id = storeId(url)
build_id=buildId(url)
url = f"https://www.rappi.com.br/_next/data/{build_id}/pt-BR/ssg/{store_id}.json"
s=45
count = 0
start_datetime = datetime.now()
formatted_time = start_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(f'STARTING SCRAPING: {formatted_time}')
#Create list of all store aisles
aisles_list = aisles(url, store_id)
count +=1
print(f'{count} REQUESTS DONE')
start_datetime = datetime.now()
formatted_time = start_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(F'AISLES_LIST DONE AT:{formatted_time}')

time.sleep(s)

#Create a dict of all subAisles of store aisles

aisles_dict = {}
for aisle in aisles_list:
    aisles_dict[aisle] = subAisles(url,aisle, store_id)
    start_datetime = datetime.now()
    formatted_time = start_datetime.strftime("%Y-%m-%d | %H:%M:%S")
    count +=1
    print(f'{count} REQUESTS DONE')
    time.sleep(s)

start_datetime = datetime.now()
formatted_starttime = start_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(f'AISLES_DICT DONE AT: {formatted_starttime}')
time.sleep(s)

#Products scraper
products_list = []
print('AISLES_LIST AND AISLES_DICT DONE')
print(f'STARTING TO SCRAPE {store_id} PRODUCTS')
for key in aisles_dict:
    aisle = key
    subAisles_list = aisles_dict[key]
    subAisle_heather = subAisles_list[0]
    request_heather = {'referer':f'https://www.rappi.com.br/lojas/{store_id}/{aisle}/{subAisle_heather}'}
    for subAisle in subAisles_list:
        sub_aisle_url = subAisleURL(url,aisle,subAisle)
        # status = check_internet_connection()
        # time.sleep(5)
        # while status != 200:
        #     print("No internet connection. Press enter to restart the program when conection is available")
        #     input()
        #     status = check_internet_connection(url)
        # if status == 200:
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
        count +=1
        print(f'{count} REQUESTS DONE')
        time.sleep(s)

    print(f'{aisle} PRODUCTS SCRAPED:{len(new_products_list)}')
        
print(f'TOTAL PRODUCTS:{len(new_products_list)}')
start_datetime = datetime.now()
formatted_starttime = start_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(f'TOTAL PRODUCTS DONE AT: {formatted_starttime}')

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
end_datetime = datetime.now()
formatted_endtime = start_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(formatted_endtime)





