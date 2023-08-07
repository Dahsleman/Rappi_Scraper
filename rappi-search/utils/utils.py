import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
import geocoder 
import subprocess
from unidecode import unidecode

search_dict = {}
new_products_list = []
datetime_products_list = []
new_error_list = []

# Define the Node.js code as a string
node_code = """
const puppeteer = require('puppeteer');
async function scrapeNetworkRequests() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setRequestInterception(true);
  try{
  page.on('request', (request) => {
    if (request.method() == 'POST' && request.url() == 'https://services.rappi.com.br/api/pns-global-search-api/v1/unified-recent-top-searches') {
      const headersJson = JSON.stringify(request.headers(), null, 2);
      const headers = JSON.parse(headersJson);
      const authorization = headers.authorization;
      console.log(authorization); 
      process.exit();
    }
    request.continue();
  });
  await page.goto('https://www.rappi.com.br/');
  await page.waitForNavigation();
  await browser.close();
  } catch (error){
    console.error('An error occurred:', error);
  }
}
scrapeNetworkRequests();
"""

def result():
  authorization = subprocess.run(['node', '-e', node_code], capture_output=True, text=True)
  return authorization

def update_xlsx_with_address(xlsx_file, address):
    # Create a new dataframe with the address
    df = pd.DataFrame({'Address': [address]})
    # Write the dataframe to the Excel file
    with pd.ExcelWriter(xlsx_file, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name='Address', index=False)
        print("xlsx updated with client address.")

def update_xlsx_with_json(json_file, xlsx_file, sheet_name):
    # Read the JSON file into a dataframe
    df = pd.read_json(json_file)
    # Write the dataframe to the Excel file
    with pd.ExcelWriter(xlsx_file, engine='openpyxl', mode='a') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        print("xlsx updated with erros.")

def create_xlsx_with_json(json_file, xlsx_file, sheet_name):
    # Read the JSON file into a dataframe
    df = pd.read_json(json_file)  
    # Create a new Excel file
    try:
        with pd.ExcelWriter(xlsx_file) as writer:
            # Write the dataframe to the Excel sheet
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print("xlsx created.")
    except PermissionError:
        print(f'ERROR: please close {xlsx_file} and run again')
        exit()

def productsList(response:requests.models.Response, term:str, store_id:str, store_type:str, unit:str, keywords:tuple)->list:
    master_list=[]
    products_dict = {}
    products_list = []

    soup = BeautifulSoup(response.content, "html.parser")
    #creating products_dict
    i=0
    li_tags = soup.find_all("li")
    for tag in li_tags:
        data_qa=tag.get("data-qa")
        if data_qa is not None and data_qa.rfind("product-item") != -1:
            products_dict = {}
            products_dict['k term']= term
            products_dict['k unit-input']= unit
            products_dict['store-id'] = store_id
            products_dict['store-type'] = store_type
            products_list.append(products_dict)
            i+=1

    # get product_id
    i=0
    div_tags = soup.find_all("div")
    for tag in div_tags:
        data_qa=tag.get("data-qa")
        if data_qa is not None and data_qa.rfind("product-item") != -1:
            products_dict = products_list[i]
            product_id = data_qa.replace(f"product-item-", "")
            products_dict['product-id'] = product_id
            i+=1

    #get master_product_id
    a_tags = soup.find_all("a")
    for tag in a_tags:
        href=tag.get("href")
        if href is not None and href.rfind("/p/") != -1:
            start_index = href.rfind("-") + 1  
            end_index = href.rfind("") 
            if start_index != -1 and end_index != -1:
                master_product_id = href[start_index:end_index]
                if master_product_id not in master_list:
                    master_list.append(master_product_id)
            # print(master_product_id) #esta pegando duas vezes, precisa de somente 1
    i=0
    for id in master_list:
        products_dict = products_list[i]
        products_dict['master-product-id'] = id
        i+=1

    #get product_price and product_real_price
    i=0
    span_tags = soup.find_all("span")
    for tag in span_tags:
        data_qa=tag.get("data-qa")
        if data_qa == 'product-price':
            products_dict = products_list[i]
            product_price_string = tag.string
            product_price_substrings = product_price_string.split(" ")
            product_price_string = product_price_substrings[1]
            if product_price_string.rfind("/") == -1:
                if product_price_string.rfind(".") == -1:
                    product_price_string = product_price_string.replace(",", ".")
                else:
                    product_price_string = product_price_string.replace(".", "")
                    product_price_string = product_price_string.replace(",", ".")
            else:
                product_price_substrings.clear()
                product_price_substrings = product_price_string.split("/")
                product_price_string = product_price_substrings[0]
                if product_price_string.rfind(".") == -1:
                    product_price_string = product_price_string.replace(",", ".")
                else:
                    product_price_string = product_price_string.replace(".", "")
                    product_price_string = product_price_string.replace(",", ".")
                
            product_price = float(product_price_string)
            products_dict['product-price'] = product_price
        elif data_qa == 'product-real-price':
            product_real_price_string = tag.string
            
            products_dict = products_list[i]
            if product_real_price_string is None:
                product_real_price = product_price
                products_dict['product-real-price'] = product_real_price
            else:
                product_real_price_substrings = product_real_price_string.split(" ")
                product_real_price_string = product_real_price_substrings[1]
                if product_real_price_string.rfind("/") == -1:
                    if product_real_price_string.rfind(".") == -1:
                        product_real_price_string = product_real_price_string.replace(",", ".")
                    else:
                        product_real_price_string = product_real_price_string.replace(".", "")
                        product_real_price_string = product_real_price_string.replace(",", ".")
                else:
                    product_real_price_substrings.clear()
                    product_real_price_substrings = product_real_price_string.split("/")
                    product_real_price_string = product_real_price_substrings[0]
                    if product_real_price_string.rfind(".") == -1:
                        product_real_price_string = product_real_price_string.replace(",", ".")
                    else:
                        product_real_price_string = product_real_price_string.replace(".", "")
                        product_real_price_string = product_real_price_string.replace(",", ".")

                product_real_price = float(product_real_price_string)
                products_dict['product-real-price'] = product_real_price
            i+=1

    # get product_unit
    i=0
    span_tags = soup.find_all("span")
    for tag in span_tags:
        data_qa=tag.get("data-qa")            
        if data_qa == 'product-pum':
            products_dict = products_list[i]
            product_unit_string = tag.string
            substrings_unit = product_unit_string.split("/")
            product_unit = substrings_unit[0]
            product_unit = product_unit.replace("(","")
            product_unit_index = substrings_unit[1]
            product_unit_index = product_unit_index.replace(")","")
            product_price = products_dict['product-price']
            
            products_dict['product-unit'] = product_unit_string

            product_size = f"{round(product_price/float(product_unit))}"
            product_vol = f"{product_size} {product_unit_index}"
            products_dict['k product-size'] = product_vol
             
            if product_unit_index == unit:
                products_dict['k unit-input-size'] = float(f"{product_size}")
                products_dict['k product-input-unit'] = product_unit_string
                products_dict['k product-input-price'] = float(product_unit)
                products_dict['k match-unit-input?'] = "True"
            else:
                if product_unit_index == "kg":
                    if unit == "gr":
                        products_dict['k unit-input-size'] = float(f"{float(product_size)*1000}")
                        product_new_unit = float(product_unit)/1000
                        product_new_unit = f"{product_new_unit:.4f}"
                        products_dict['k product-input-unit'] = f"({product_new_unit}/{unit})"
                        products_dict['k product-input-price'] = float(product_new_unit)
                    elif unit == "ml" or unit == "l" or unit == "und":
                        products_dict['k unit-input-size'] = "incompativel"
                        products_dict['k product-input-unit'] = "incompativel"
                        products_dict['k product-input-price'] = "incompativel"
                    products_dict['k match-unit-input?'] = "False"
                elif product_unit_index == "gr":
                    if unit == "kg":
                        products_dict['k unit-input-size'] = float(f"{float(product_size)/1000}")
                        product_new_unit = float(product_unit)*1000
                        product_new_unit = f"{product_new_unit:.2f}"
                        products_dict['k product-input-unit'] = f"({product_new_unit}/{unit})"
                        products_dict['k product-input-price'] = float(product_new_unit)
                    elif unit == "ml" or unit == "l" or unit == "und":
                        products_dict['k unit-input-size'] = "incompativel"
                        products_dict['k product-input-unit'] = "incompativel"
                        products_dict['k product-input-price'] = "incompativel"
                    products_dict['k match-unit-input?'] = "False"
                elif product_unit_index == "l":
                    if unit == "ml":
                        products_dict['k unit-input-size'] = float(f"{float(product_size)*1000}")
                        product_new_unit = float(product_unit)/1000
                        product_new_unit = f"{product_new_unit:.4f}"
                        products_dict['k product-input-unit'] = f"({product_new_unit}/{unit})"
                        products_dict['k product-input-price'] = float(product_new_unit)
                    elif unit == "kg" or unit == "gr" or unit == "und":
                        products_dict['k unit-input-size'] = "incompativel"
                        products_dict['k product-input-unit'] = "incompativel"
                        products_dict['k product-input-price'] = "incompativel"
                    products_dict['k match-unit-input?'] = "False"        
                elif product_unit_index == "ml":
                    if unit == "l":
                        products_dict['k unit-input-size'] = float(f"{float(product_size)/1000}")
                        product_new_unit = float(product_unit)*1000
                        product_new_unit = f"{product_new_unit:.2f}"
                        products_dict['k product-input-unit'] = f"({product_new_unit}/{unit})"
                        products_dict['k product-input-price'] = float(product_new_unit)
                    elif unit == "kg" or unit == "gr" or unit == "und":
                        products_dict['k unit-input-size'] = "incompativel"
                        products_dict['k product-input-unit'] = "incompativel"
                        products_dict['k product-input-price'] = "incompativel"
                    products_dict['k match-unit-input?'] = "False"
                elif product_unit_index == "und":
                    if unit == "kg" or unit == "gr" or unit == "l" or unit == "ml":
                        products_dict['k unit-input-size'] = "incompativel"
                        products_dict['k product-input-unit'] = "incompativel"
                        products_dict['k product-input-price'] = "incompativel"
                        products_dict['k match-unit-input?'] = "False"
                else:
                    products_dict['k unit-input-size'] = "nao cadastrado"
                    products_dict['k product-input-unit'] = "nao cadastrado"
                    products_dict['k product-input-price'] = "nao cadastrado"
                    products_dict['k match-unit-input?'] = "False"
            i+=1

    #get product_name
    i=0
    h3_tags = soup.find_all("h3")
    for tag in h3_tags:
        data_qa=tag.get("data-qa")
        if data_qa == 'product-name':
            products_dict = products_list[i]
            product_name = tag.string
            products_dict['product-name'] = product_name
            #match product name and query name
            #remove accents from product_name string
            product_name = unidecode(product_name)
            #make product_name lower case
            product_name = product_name.lower()
            product_name_list = product_name.split(" ")
            #remove accents from term string
            term = unidecode(term)
            #make term lower case
            term = term.lower()
            term_list = term.split(" ")
            q = len(term_list)
            y = 0
            for item in term_list:
                if item in product_name_list:
                    y+=1                    
            if y == q:
                products_dict['k term-in-product-name?'] = 'True'
            else:
                products_dict['k term-in-product-name?'] = 'False'            
            z = 0
            while z < len(keywords):
                keyword = keywords[z]
                keyword = unidecode(keyword)
                keyword = keyword.lower()
                keyword_list = keyword.split(" ")
                q = len(keyword_list)
                y = 0
                for item in keyword_list:
                    if item in product_name_list:
                        y+=1                    
                if y == q:
                    products_dict['k term-in-product-name?'] = 'False'
                z = z + 1
            i+=1
    return products_list

def products_scraper(store:str, term:str, unit:str, keywords:tuple)->tuple:
    error_list = []
    products_list = []
    error_dict = {}
    substrings = store.split("-")
    store_id = substrings[0]
    substrings.pop(0)
    store_type = ""
    for substring in substrings:
        if len(store_type) == 0:
            store_type=substring
        else:
            store_type+=f"-{substring}"
 
    url = f"https://www.rappi.com.br/lojas/{store}/s?term={term}"

    request_heather = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}

    try:
        response = requests.get(url, headers=request_heather)
        response.raise_for_status()
        if response.status_code == 200:
            term = term.replace('%20',' ')
            products_list = productsList(response, term, store_id, store_type, unit, keywords)
            error_dict['error'] = ""
            error_dict['query'] = ""
            error_dict['store'] = ""
            error_dict['url'] = ""
            error_list.append(error_dict)
            return products_list, error_list          
        else:
            print(f"ERROR: {response.status_code}")
            term = term.replace('%20',' ')
            error_dict['error'] = response.status_code
            error_dict['query'] = term
            error_dict['store'] = store
            error_dict['url'] = url
            error_list.append(error_dict)
            return products_list, error_list
    except requests.exceptions.HTTPError as err:
        if response.status_code == 429:
            print(f'TOO MANY PRODUCTS REQUESTS: WAIT 60s')
            time.sleep(60)
            try:
                response = requests.get(url, headers=request_heather)
                response.raise_for_status()
                if response.status_code == 200:
                    term = term.replace('%20',' ')
                    products_list = productsList(response, term, store_id, store_type, unit, keywords)
                    error_dict['error'] = ""
                    error_dict['query'] = ""
                    error_dict['store'] = ""
                    error_dict['url'] = ""
                    error_list.append(error_dict)
                    return products_list, error_list
                else:
                    print(f"ERROR: {response.status_code}")
                    term = term.replace('%20',' ')
                    error_dict['error'] = response.status_code
                    error_dict['query'] = term
                    error_dict['store'] = store
                    error_dict['url'] = url
                    error_list.append(error_dict)
                    return products_list, error_list
            except requests.exceptions.RequestException as err:
                err = str(err)
                term = term.replace('%20',' ')
                error_dict['error'] = err
                error_dict['query'] = term
                error_dict['store'] = store
                error_dict['url'] = url
                error_list.append(error_dict)
                return products_list, error_list
        elif response.status_code == 502:
            print(f'BAD GATEWAY: LETS TRY AGAIN IN 30s')
            time.sleep(30)
            try:
                response = requests.get(url, headers=request_heather)
                response.raise_for_status()
                if response.status_code == 200:
                    term = term.replace('%20',' ')
                    products_list = productsList(response, term, store_id, store_type, unit, keywords)
                    error_dict['error'] = ""
                    error_dict['query'] = ""
                    error_dict['store'] = ""
                    error_dict['url'] = ""
                    error_list.append(error_dict)
                    return products_list, error_list
                else:
                    print(f"ERROR: {response.status_code}")
                    term = term.replace('%20',' ')
                    error_dict['error'] = response.status_code
                    error_dict['query'] = term
                    error_dict['store'] = store
                    error_dict['url'] = url
                    error_list.append(error_dict)
                    return products_list, error_list       
            except requests.exceptions.RequestException as err:
                err = str(err)
                term = term.replace('%20',' ')
                error_dict['error'] = err
                error_dict['query'] = term
                error_dict['store'] = store
                error_dict['url'] = url
                error_list.append(error_dict)
                return products_list, error_list          
        else:
            print(f"ERROR: {response.status_code}")
            term = term.replace('%20',' ')
            error_dict['error'] = response.status_code
            error_dict['query'] = term
            error_dict['store'] = store
            error_dict['url'] = url
            error_list.append(error_dict)
            return products_list, error_list
             
    except requests.exceptions.RequestException as err:
        err = str(err)
        print(f"An error occurred during the request: {err}")
        term = term.replace('%20',' ')
        error_dict['error'] = err
        error_dict['query'] = term
        error_dict['store'] = store
        error_dict['url'] = url
        error_list.append(error_dict)
        return products_list, error_list
    
def storesList(lat, lng, query, bearer_token):
    stores_list = []
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
    
    try:
        response = requests.post(url, json=payload, headers=request_heathers)
        response.raise_for_status()
        if response.status_code == 200:
            json_data = response.json()
            stores = json_data['stores']
            for store in stores:
                store_id = store['store_id']
                store_type = store['store_type']
                store_type = store_type.replace("_","-")
                store_url = f"{store_id}-{store_type}"
                stores_list.append(store_url)
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