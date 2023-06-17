import json
import csv
import json
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd

def update_xlsx(json_file, xlsx_file, sheet_name):
   # Load the JSON data
    with open(json_file, 'r') as f:
        json_data = f.read()
    
    # Create a DataFrame from the JSON data
    df = pd.read_json(json_data)
    
    # Open the existing CSV file
    with pd.ExcelWriter(xlsx_file, mode='a', engine='openpyxl') as writer:
        # Write the DataFrame to a new sheet in the CSV file
        df.to_excel(writer, sheet_name=sheet_name, index=False)

def create_xlsx(json_file, xlsx_file, sheet_name):
    # Read the JSON file into a dataframe
    df = pd.read_json(json_file)
    
    # Create a new Excel file
    with pd.ExcelWriter(xlsx_file) as writer:
        # Write the dataframe to the Excel sheet
        df.to_excel(writer, sheet_name=sheet_name, index=False)

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
    elif response.status_code == 429:
        print(f'TOO MANY REQUESTS: WAIT {s}s')
        time.sleep(s)
        response = requests.get(url)
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
unvalid_urls = []
s = 60
build_id = ""

# URLS of the webpage to scrape
client="Athos"

urls = ["https://www.rappi.com.br/lojas/900134659-verdemar/Cuidado-pessoal/Desodorantes","https://www.rappi.com.br/lojas/900134659-verdemar/hortifruti/polpa","https://www.rappi.com.br/lojas/900134659-verdemar/Congelados-e-refrigerados/Comidas-prontas","https://www.rappi.com.br/lojas/900134659-verdemar/hortifruti/frutas","https://www.rappi.com.br/lojas/900134659-verdemar/Laticanios-e-ovos/Bebidas-vegetais","https://www.rappi.com.br/lojas/900134659-verdemar/Laticanios-e-ovos/Iogurte","https://www.rappi.com.br/lojas/900134659-verdemar/padaria-e-confeitaria/torradas","https://www.rappi.com.br/lojas/900134659-verdemar/Laticanios-e-ovos/Leite","https://www.rappi.com.br/lojas/900134659-verdemar/Limpeza/Limpadores","https://www.rappi.com.br/lojas/900134659-verdemar/Cuidados-com-roupas-e-sapatos/Detergentes","https://www.rappi.com.br/lojas/900134659-verdemar/Limpeza/Desinfetante","https://www.rappi.com.br/lojas/900134659-verdemar/Acougue-e-peixaria/Outras-carnes","https://www.rappi.com.br/lojas/900134659-verdemar/Acougue-e-peixaria/Bovinos","https://www.rappi.com.br/lojas/900309095-supermercado-dia/Cuidado-pessoal/Desodorantes","https://www.rappi.com.br/lojas/900309095-supermercado-dia/hortifruti/polpa","https://www.rappi.com.br/lojas/900309095-supermercado-dia/Congelados-e-refrigerados/Comidas-prontas","https://www.rappi.com.br/lojas/900309095-supermercado-dia/hortifruti/frutas","https://www.rappi.com.br/lojas/900309095-supermercado-dia/Laticanios-e-ovos/Bebidas-vegetais","https://www.rappi.com.br/lojas/900309095-supermercado-dia/Laticanios-e-ovos/Iogurte","https://www.rappi.com.br/lojas/900309095-supermercado-dia/padaria-e-confeitaria/torradas","https://www.rappi.com.br/lojas/900309095-supermercado-dia/Laticanios-e-ovos/Leite","https://www.rappi.com.br/lojas/900309095-supermercado-dia/Limpeza/Limpadores","https://www.rappi.com.br/lojas/900309095-supermercado-dia/Cuidados-com-roupas-e-sapatos/Detergentes","https://www.rappi.com.br/lojas/900309095-supermercado-dia/Limpeza/Desinfetante","https://www.rappi.com.br/lojas/900309095-supermercado-dia/Acougue-e-peixaria/Outras-carnes","https://www.rappi.com.br/lojas/900309095-supermercado-dia/Acougue-e-peixaria/Bovinos","https://www.rappi.com.br/lojas/900306746-carrefour-esp-super-market/Cuidado-pessoal/Desodorantes","https://www.rappi.com.br/lojas/900306746-carrefour-esp-super-market/hortifruti/polpa","https://www.rappi.com.br/lojas/900306746-carrefour-esp-super-market/Congelados-e-refrigerados/Comidas-prontas","https://www.rappi.com.br/lojas/900306746-carrefour-esp-super-market/hortifruti/frutas","https://www.rappi.com.br/lojas/900306746-carrefour-esp-super-market/Laticanios-e-ovos/Bebidas-vegetais","https://www.rappi.com.br/lojas/900306746-carrefour-esp-super-market/Laticanios-e-ovos/Iogurte","https://www.rappi.com.br/lojas/900306746-carrefour-esp-super-market/padaria-e-confeitaria/torradas","https://www.rappi.com.br/lojas/900306746-carrefour-esp-super-market/Laticanios-e-ovos/Leite","https://www.rappi.com.br/lojas/900306746-carrefour-esp-super-market/Limpeza/Limpadores","https://www.rappi.com.br/lojas/900306746-carrefour-esp-super-market/Cuidados-com-roupas-e-sapatos/Detergentes","https://www.rappi.com.br/lojas/900306746-carrefour-esp-super-market/Limpeza/Desinfetante","https://www.rappi.com.br/lojas/900306746-carrefour-esp-super-market/Acougue-e-peixaria/Outras-carnes","https://www.rappi.com.br/lojas/900306746-carrefour-esp-super-market/Acougue-e-peixaria/Bovinos","https://www.rappi.com.br/lojas/900649271-super-abc/Cuidado-pessoal/Desodorantes","https://www.rappi.com.br/lojas/900649271-super-abc/hortifruti/polpa","https://www.rappi.com.br/lojas/900649271-super-abc/Congelados-e-refrigerados/Comidas-prontas","https://www.rappi.com.br/lojas/900649271-super-abc/hortifruti/frutas","https://www.rappi.com.br/lojas/900649271-super-abc/Laticanios-e-ovos/Bebidas-vegetais","https://www.rappi.com.br/lojas/900649271-super-abc/Laticanios-e-ovos/Iogurte","https://www.rappi.com.br/lojas/900649271-super-abc/padaria-e-confeitaria/torradas","https://www.rappi.com.br/lojas/900649271-super-abc/Laticanios-e-ovos/Leite","https://www.rappi.com.br/lojas/900649271-super-abc/Limpeza/Limpadores","https://www.rappi.com.br/lojas/900649271-super-abc/Cuidados-com-roupas-e-sapatos/Detergentes","https://www.rappi.com.br/lojas/900649271-super-abc/Limpeza/Desinfetante","https://www.rappi.com.br/lojas/900649271-super-abc/Acougue-e-peixaria/Outras-carnes","https://www.rappi.com.br/lojas/900649271-super-abc/Acougue-e-peixaria/Bovinos","https://www.rappi.com.br/lojas/900130001-carrefour-hiper-super-market/Cuidado-pessoal/Desodorantes","https://www.rappi.com.br/lojas/900130001-carrefour-hiper-super-market/hortifruti/polpa","https://www.rappi.com.br/lojas/900130001-carrefour-hiper-super-market/Congelados-e-refrigerados/Comidas-prontas","https://www.rappi.com.br/lojas/900130001-carrefour-hiper-super-market/hortifruti/frutas","https://www.rappi.com.br/lojas/900130001-carrefour-hiper-super-market/Laticanios-e-ovos/Bebidas-vegetais","https://www.rappi.com.br/lojas/900130001-carrefour-hiper-super-market/Laticanios-e-ovos/Iogurte","https://www.rappi.com.br/lojas/900130001-carrefour-hiper-super-market/padaria-e-confeitaria/torradas","https://www.rappi.com.br/lojas/900130001-carrefour-hiper-super-market/Laticanios-e-ovos/Leite","https://www.rappi.com.br/lojas/900130001-carrefour-hiper-super-market/Limpeza/Limpadores","https://www.rappi.com.br/lojas/900130001-carrefour-hiper-super-market/Cuidados-com-roupas-e-sapatos/Detergentes","https://www.rappi.com.br/lojas/900130001-carrefour-hiper-super-market/Limpeza/Desinfetante","https://www.rappi.com.br/lojas/900130001-carrefour-hiper-super-market/Acougue-e-peixaria/Outras-carnes","https://www.rappi.com.br/lojas/900130001-carrefour-hiper-super-market/Acougue-e-peixaria/Bovinos","https://www.rappi.com.br/lojas/900631003-carrefour-big-hiper-nc/Cuidado-pessoal/Desodorantes","https://www.rappi.com.br/lojas/900631003-carrefour-big-hiper-nc/hortifruti/polpa","https://www.rappi.com.br/lojas/900631003-carrefour-big-hiper-nc/Congelados-e-refrigerados/Comidas-prontas","https://www.rappi.com.br/lojas/900631003-carrefour-big-hiper-nc/hortifruti/frutas","https://www.rappi.com.br/lojas/900631003-carrefour-big-hiper-nc/Laticanios-e-ovos/Bebidas-vegetais","https://www.rappi.com.br/lojas/900631003-carrefour-big-hiper-nc/Laticanios-e-ovos/Iogurte","https://www.rappi.com.br/lojas/900631003-carrefour-big-hiper-nc/padaria-e-confeitaria/torradas","https://www.rappi.com.br/lojas/900631003-carrefour-big-hiper-nc/Laticanios-e-ovos/Leite","https://www.rappi.com.br/lojas/900631003-carrefour-big-hiper-nc/Limpeza/Limpadores","https://www.rappi.com.br/lojas/900631003-carrefour-big-hiper-nc/Cuidados-com-roupas-e-sapatos/Detergentes","https://www.rappi.com.br/lojas/900631003-carrefour-big-hiper-nc/Limpeza/Desinfetante","https://www.rappi.com.br/lojas/900631003-carrefour-big-hiper-nc/Acougue-e-peixaria/Outras-carnes","https://www.rappi.com.br/lojas/900631003-carrefour-big-hiper-nc/Acougue-e-peixaria/Bovinos","https://www.rappi.com.br/lojas/900137947-carrefour-hiper-express-market/Cuidado-pessoal/Desodorantes","https://www.rappi.com.br/lojas/900137947-carrefour-hiper-express-market/hortifruti/polpa","https://www.rappi.com.br/lojas/900137947-carrefour-hiper-express-market/Congelados-e-refrigerados/Comidas-prontas","https://www.rappi.com.br/lojas/900137947-carrefour-hiper-express-market/hortifruti/frutas","https://www.rappi.com.br/lojas/900137947-carrefour-hiper-express-market/Laticanios-e-ovos/Bebidas-vegetais","https://www.rappi.com.br/lojas/900137947-carrefour-hiper-express-market/Laticanios-e-ovos/Iogurte","https://www.rappi.com.br/lojas/900137947-carrefour-hiper-express-market/padaria-e-confeitaria/torradas","https://www.rappi.com.br/lojas/900137947-carrefour-hiper-express-market/Laticanios-e-ovos/Leite","https://www.rappi.com.br/lojas/900137947-carrefour-hiper-express-market/Limpeza/Limpadores","https://www.rappi.com.br/lojas/900137947-carrefour-hiper-express-market/Cuidados-com-roupas-e-sapatos/Detergentes","https://www.rappi.com.br/lojas/900137947-carrefour-hiper-express-market/Limpeza/Desinfetante","https://www.rappi.com.br/lojas/900137947-carrefour-hiper-express-market/Acougue-e-peixaria/Outras-carnes","https://www.rappi.com.br/lojas/900137947-carrefour-hiper-express-market/Acougue-e-peixaria/Bovinos"]

for url in urls:
    url = url.lower()
    referer = url
    if build_id == "":
        build_id=buildId(url)
    url_dict = search(url)
    sub_aisle = url_dict['sub_aisle']
    aisle = url_dict['aisle']
    store = url_dict['store']
    url = f"https://www.rappi.com.br/_next/data/{build_id}/pt-BR/ssg/{store}/{aisle}/{sub_aisle}.json"
    requests_dict[url] = referer
    url_dict.clear

print('STARTING SCRAPING')
for url,referer in requests_dict.items():
    url_dict = search(referer)
    sub_aisle = url_dict['sub_aisle']
    aisle = url_dict['aisle']
    store = url_dict['store']    
    request_heather = {'referer':f'{referer}'}
    response = requests.get(url, headers=request_heather)

    if response.status_code == 200:
        json_data = response.json()
    elif response.status_code == 429:
        print(f'TOO MANY PRODUCTS REQUESTS: WAIT {s}s')
        time.sleep(s)
        response = requests.get(url, headers=request_heather)
        json_data = response.json()
    elif response.status_code == 502:
        print(f'BAD GATEWAY: WAIT {s}s')
        response = requests.get(url, headers=request_heather)
        json_data = response.json()
    else:
        print(f"ERROR: {response.status_code}")
    try:
        pageProps = json_data['pageProps']
        try:
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
        except:
            unvalid_urls.append(referer)
    except:
        unvalid_urls.append(referer)
    
#add datetime 
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d | %H:%M:%S")
for product in products_list:
    items = list(product.items())
    items.insert(0, ('collected_at', formatted_datetime))
    product = dict(items)
    new_products_list.append(product)
  
print(f'TOTAL PRODUCTS SCRAPED: {len(new_products_list)}')
print(f'TOTAL UNVALID URLS: {len(unvalid_urls)}')

# Create json_file of products.
jsonFile = f'Rappi_{client}'
with open(f'{jsonFile}.json', 'w') as fp:
    json.dump(new_products_list, fp, indent=4)

# Create json_file of unvailed URL's.
jsonFile_urls = f'Rappi_{client}_unvalid_URLs'
with open(f'{jsonFile_urls}.json', 'w') as fp:
    json.dump(unvalid_urls, fp, indent=4)

# Create xlsx file
json_file = f'{jsonFile}.json'
xlsx_file = f'Rappi_{client}.xlsx'
sheet_name = 'Products'
create_xlsx(json_file, xlsx_file, sheet_name)
print("xlsx file created.")

# Update xlsx file
json_file = f'{jsonFile_urls}.json'
sheet_name = 'unvalid_urls'
update_xlsx(json_file, xlsx_file, sheet_name)

# Create the cvs file
json_file_path = f'{jsonFile}.json'
with open(json_file_path, "r") as json_file:
    json_data = json.load(json_file)

# # Extract the headers from the first JSON object
# headers = list(json_data[0].keys())

# csv_file_path = f'Rappi_{client}.csv'
# # Write the JSON data to a CSV file
# with open(csv_file_path, "w", encoding="utf-8", newline="") as csv_file:
#     writer = csv.DictWriter(csv_file, fieldnames=headers)

#     # Write the header row
#     writer.writeheader()

#     # Write the data rows
#     writer.writerows(json_data)

# print("CSV file created.")

