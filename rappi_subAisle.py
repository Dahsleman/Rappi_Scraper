import json
import csv
import json
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup

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
         
def search(url:str)->dict:
    string_dict = {}
    """find sub_aisle"""
    start_index = url.rfind("/") + 1 
    end_index = url.rfind("") 
    if start_index != -1 and end_index != -1:
        sub_aisle = url[start_index:end_index]
        string_dict['sub_aisle'] = sub_aisle 
    else:
        return print("Subaisle not found in the string.")

    """find aisle"""
    string = url.replace(f"/{sub_aisle}", "")
    start_index = string.rfind("/") + 1 
    end_index = string.rfind("")  
    if start_index != -1 and end_index != -1:
        aisle = url[start_index:end_index]
        string_dict['aisle'] = aisle 
    else:
        return print("Aisle not found in the string.")

    """find store"""
    string = url.replace(f"/{aisle}/{sub_aisle}", "")
    start_index = string.rfind("/") + 1 
    end_index = string.rfind("")  
    if start_index != -1 and end_index != -1:
        store = url[start_index:end_index]
        string_dict['store'] = store 
    else:
        return print("Store not found in the string.")
    
    return string_dict

requests_dict = {}
products_list = []
new_products_list = []
s = 60

# URLS of the webpage to scrape
client="Luis"
urls = [
    "https://www.rappi.com.br/lojas/900155885-supermercado-dia/laticinios-e-ovos/manteiga-e-margarina",
    "https://www.rappi.com.br/lojas/900027422-verdemar/hortifruti/polpa"
]

for url in urls:
    referer = url
    build_id=buildId(url)
    url_dict = search(url)
    sub_aisle = url_dict['sub_aisle']
    aisle = url_dict['aisle']
    store = url_dict['store']
    url = f"https://www.rappi.com.br/_next/data/{build_id}/pt-BR/ssg/{store}/{aisle}/{sub_aisle}.json"
    requests_dict[url] = referer
    url_dict.clear

for url,referer in requests_dict.items():
    url_dict = search(referer)
    sub_aisle = url_dict['sub_aisle']
    aisle = url_dict['aisle']
    store = url_dict['store']    
    request_heather = {'referer':f'{referer}'}
    response = requests.get(url, headers=request_heather)

    if response.status_code == 429:
        print(f'TOO MANY PRODUCTS REQUESTS: WAIT {s}s')
        time.sleep(s)
        response = requests.get(url, headers=request_heather)
        json_data = response.json()
    elif response.status_code == 502:
        print(f'BAD GATEWAY: WAIT {s}s')
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
    url_dict.clear
    
#add datetime 
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")
for product in products_list:
    items = list(product.items())
    items.insert(0, ('collected_at', formatted_datetime))
    product = dict(items)
    new_products_list.append(product)
print(f'TOTAL PRODUCTS SCRAPED: {len(products_list)}')    
print(f'TOTAL NEW PRODUCTS SCRAPED: {len(new_products_list)}')

# Create json_file.
jsonFile = f'Rappi_{client}'
with open(f'{jsonFile}.json', 'w') as fp:
    json.dump(new_products_list, fp, indent=4)

json_file_path = f'{jsonFile}.json'
# Read the JSON file
with open(json_file_path, "r") as json_file:
    json_data = json.load(json_file)

# Extract the headers from the first JSON object
headers = list(json_data[0].keys())

csv_file_path = f'Rappi_{client}.csv'
# Write the JSON data to a CSV file
with open(csv_file_path, "w", encoding="utf-8", newline="") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=headers)

    # Write the header row
    writer.writeheader()

    # Write the data rows
    writer.writerows(json_data)

print("CSV file created.")
