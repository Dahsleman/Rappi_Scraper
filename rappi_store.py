import json
import requests
import time
import re
import csv
from datetime import datetime
import socket
from bs4 import BeautifulSoup
import pandas as pd

def create_xlsx(json_file, xlsx_file, sheet_name):
    # Read the JSON file into a dataframe
    df = pd.read_json(json_file)
    
    # Create a new Excel file
    with pd.ExcelWriter(xlsx_file) as writer:
        # Write the dataframe to the Excel sheet
        df.to_excel(writer, sheet_name=sheet_name, index=False)

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

def buildId(store_id):
    url = f"https://www.rappi.com.br/lojas/{store_id}/catalogo"
    urls = []
    request_heather = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=request_heather)
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

def aisles(url:str, store_id:str)->list:
    """return an aisles list of a given store"""
    aisles_list=[]
    referer = f'https://www.rappi.com.br/lojas/{store_id}/catalogo'
    request_heather = {
        'referer':referer, 
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
    response = requests.get(url, headers=request_heather)
    if response.status_code == 429:
        print('TOO MANY REQUESTS: WAIT 1m')
        time.sleep(60)
        print('REQUESTS STARTED')
        response = requests.get(url, headers=request_heather)
        json_data = response.json()
    else:
        json_data = response.json()

    try:
        pageProps = json_data['pageProps']
        try:
            fallback = pageProps['fallback']
            storefront = fallback[f'storefront/{store_id}']
            aisles_tree_response = storefront['aisles_tree_response']
            data = aisles_tree_response['data']
            components = data['components']

            for component in components:
                resource = component['resource']
                aisle = resource['friendly_url']
                aisles_list.append(aisle)
        except:
            url = referer
            request_heather = {
                'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=request_heather)
            soup = BeautifulSoup(response.content, "html.parser")
            #get product_item
            a_tags = soup.find_all("a")
            for tag in a_tags:
                href=tag.get("href")
                if href is not None and href.rfind(f"/lojas/{store_id}/") != -1:
                    if href.rfind(f"/lojas/{store_id}/catalogo") == -1:
                        aisle = href.replace(f"/lojas/{store_id}/","")
                        aisles_list.append(aisle)
    except:
        url = referer
        request_heather = {
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=request_heather)
        soup = BeautifulSoup(response.content, "html.parser")
        #get product_item
        a_tags = soup.find_all("a")
        for tag in a_tags:
            href=tag.get("href")
            if href is not None and href.rfind(f"/lojas/{store_id}/") != -1:
                if href.rfind(f"/lojas/{store_id}/catalogo") == -1:
                    aisle = href.replace(f"/lojas/{store_id}/","")
                    aisles_list.append(aisle)
    
    return aisles_list

def subAisles(url:str, aisle:str, store_id:str)->list:
    """return a subAisles list of a given store aisle"""
    sub_aisles_list=[]
    aisle_url=aisleURL(url, aisle)
    request_heather = {'referer':f'https://www.rappi.com.br/lojas/{store_id}/catalogo', 'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
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

def subAisles_dict(aisles_list:list)->dict:
    #Create a dict of all subAisles of store aisles
    aisles_dict={}
    if len(aisles_list) != 0:
        for aisle in aisles_list:
            aisles_dict[aisle] = subAisles(url,aisle, store)
    return aisles_dict
    
stores_list = []
stores_dict = {}

client = "KOUMPRU"
stores = [
    "900130001-carrefour-hiper-super-market",
    "900398040-raia-market-belo-horizonte",
]

start_datetime = datetime.now()
formatted_time = start_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(f'STARTING SCRAPING: {formatted_time}')


#Create stores_dict
for store in stores:
    build_id=buildId(store)
    url = f"https://www.rappi.com.br/_next/data/{build_id}/pt-BR/ssg/{store}.json"

    #Create list of all store aisles
    aisles_list = aisles(url, store)
    aisles_dict = subAisles_dict(aisles_list)
    stores_dict[store] = aisles_dict
    
# print(stores_dict)
# print(stores_dict["900398040-raia-market-belo-horizonte"])

# #Products scraper
products_list = []
for store_id, aisles_dict in stores_dict.items():
    print(f'STARTING TO SCRAPE {store_id} PRODUCTS')
    build_id=buildId(store_id)
    url = f"https://www.rappi.com.br/_next/data/{build_id}/pt-BR/ssg/{store_id}.json"
    for key in aisles_dict:
        aisle = key
        subAisles_list = aisles_dict[key]
        subAisle_heather = subAisles_list[0]
        request_heather = {
            'referer':f'https://www.rappi.com.br/lojas/{store_id}/{aisle}/{subAisle_heather}', 
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            }
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

    start_datetime = datetime.now()
    formatted_time = start_datetime.strftime("%Y-%m-%d | %H:%M:%S")
    print(f'{store_id} PRODUCTS SCRAPED: {formatted_time}')
        
# #add datetime 
new_products_list = []
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")
for product in products_list:
    #add formatted_datetime in the beginning of the list
    items = list(product.items())
    items.insert(0, ('collected_at', formatted_datetime))
    product = dict(items)
    new_products_list.append(product)

print(f'TOTAL PRODUCTS:{len(new_products_list)}')
start_datetime = datetime.now()
formatted_starttime = start_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(f'TOTAL PRODUCTS DONE AT: {formatted_starttime}')

# Create json_file.
jsonFile = f'Rappi_{client}'
with open(f'{jsonFile}.json', 'w') as fp:
    json.dump(new_products_list, fp, indent=4)
# print("JSON file created!") 

# Create xlsx file
json_file = f'{jsonFile}.json'
xlsx_file = f'Rappi_{client}.xlsx'
sheet_name = client
create_xlsx(json_file, xlsx_file, sheet_name)
print("xlsx file created.")

# # Read the JSON file
# json_file_path = f'{jsonFile}.json'
# with open(json_file_path, "r") as json_file:
#     json_data = json.load(json_file)

# # Extract the headers from the first JSON object
# headers = list(json_data[0].keys())

# # Write the JSON data to a CSV file
# csv_file_path = f'Rappi_{client}.csv'
# with open(csv_file_path, "w", encoding="utf-8", newline="") as csv_file:
#     writer = csv.DictWriter(csv_file, fieldnames=headers)

#     # Write the header row
#     writer.writeheader()

#     # Write the data rows
#     writer.writerows(json_data)

# print("CSV file created!") 
end_datetime = datetime.now()
formatted_endtime = start_datetime.strftime("%Y-%m-%d | %H:%M:%S")
print(formatted_endtime)





