from utils.rappi_utils import StringUtils
from input_settings import InputSettings
from unidecode import unidecode
from bs4 import BeautifulSoup
import requests
import time
import re

class RappiProductUtils:
    @staticmethod
    def getProductOutStock(li_product) -> float:
        span_product_out_stock = li_product.find("span", attrs= { "data-qa": "product-out-stock" })
        
        if span_product_out_stock is None:
            return 'False'
        else:
            return 'True'

    @staticmethod
    def convertToPrice(product_price_string) -> float:
        if not product_price_string:
            return 0
        
        if product_price_string.rfind("/") == -1:
            product_price_string = StringUtils.convertToBRPriceDotSystem(product_price_string)
        else:
            product_price_string = StringUtils.convertToBRPriceDotSystem(product_price_string.split("/")[0])

        return float(product_price_string)
    
    @staticmethod
    def getProductPrice(li_product) -> float:
        span_product_price = li_product.find("span", attrs= { "data-qa": "product-price" })

        if span_product_price.string is None or " " not in span_product_price.string:
            return 0

        return RappiProductUtils.convertToPrice(span_product_price.string.split(" ")[1])
    
    @staticmethod
    def getProductRealPrice(li_product, product_price) -> float:
        span_product_price = li_product.find("span", attrs= { "data-qa": "product-real-price" })
    
        if span_product_price.string is not None and " " in span_product_price.string:
            return RappiProductUtils.convertToPrice(span_product_price.string.split(" ")[1])

        return product_price
    
    @staticmethod
    def setProductName(li_product, products_dict, keywords, term):
        can_add = True

        span_product_name = li_product.find("h3", attrs= { "data-qa": "product-name" })

        product_name = span_product_name.string
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
        
        _keywords = keywords
        if keywords is not None and type(keywords) is not tuple:
            _keywords = [keywords]

        z = 0
        while z < len(_keywords):
            keyword = _keywords[z]
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

        if InputSettings.ONLY_MATCH_SEARCH_TERM_PRODUCTS == True:
            if products_dict['k term-in-product-name?'] == 'False':
                can_add = False
                
        return can_add

    @staticmethod
    def setProductAsIncompatible(products_dict):
        can_add = True

        products_dict['k unit-input-size'] = "incompativel"
        products_dict['k product-input-unit'] = "incompativel"
        products_dict['k product-input-price'] = "incompativel"

        if InputSettings.ONLY_COMPATIBLE_PRICES_PRODUCTS == True:
                can_add = False
        return can_add

    @staticmethod
    def setProductUnit(li_product, products_dict, product_price, unit):
        can_add = True

        span_product_price = li_product.find("span", attrs= { "data-qa": "product-pum" })
        
        if span_product_price is None:
            can_add = False
            return can_add
        
        product_unit_string = span_product_price.string
        substrings_unit = product_unit_string.split("/")
        product_unit = substrings_unit[0]
        product_unit = product_unit.replace("(","")
        product_unit_index = substrings_unit[1]
        product_unit_index = product_unit_index.replace(")","")
        
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
                    can_add = RappiProductUtils.setProductAsIncompatible(products_dict)
                products_dict['k match-unit-input?'] = "False"
            elif product_unit_index == "gr":
                if unit == "kg":
                    products_dict['k unit-input-size'] = float(f"{float(product_size)/1000}")
                    product_new_unit = float(product_unit)*1000
                    product_new_unit = f"{product_new_unit:.2f}"
                    products_dict['k product-input-unit'] = f"({product_new_unit}/{unit})"
                    products_dict['k product-input-price'] = float(product_new_unit)
                elif unit == "ml" or unit == "l" or unit == "und":
                    can_add = RappiProductUtils.setProductAsIncompatible(products_dict)
                products_dict['k match-unit-input?'] = "False"
            elif product_unit_index == "l":
                if unit == "ml":
                    products_dict['k unit-input-size'] = float(f"{float(product_size)*1000}")
                    product_new_unit = float(product_unit)/1000
                    product_new_unit = f"{product_new_unit:.4f}"
                    products_dict['k product-input-unit'] = f"({product_new_unit}/{unit})"
                    products_dict['k product-input-price'] = float(product_new_unit)
                elif unit == "kg" or unit == "gr" or unit == "und":
                    can_add = RappiProductUtils.setProductAsIncompatible(products_dict)
                products_dict['k match-unit-input?'] = "False"        
            elif product_unit_index == "ml":
                if unit == "l":
                    products_dict['k unit-input-size'] = float(f"{float(product_size)/1000}")
                    product_new_unit = float(product_unit)*1000
                    product_new_unit = f"{product_new_unit:.2f}"
                    products_dict['k product-input-unit'] = f"({product_new_unit}/{unit})"
                    products_dict['k product-input-price'] = float(product_new_unit)
                elif unit == "kg" or unit == "gr" or unit == "und":
                    can_add = RappiProductUtils.setProductAsIncompatible(products_dict)
                products_dict['k match-unit-input?'] = "False"
            elif product_unit_index == "und":
                if unit == "kg" or unit == "gr" or unit == "l" or unit == "ml":
                    can_add = RappiProductUtils.setProductAsIncompatible(products_dict)
                    products_dict['k match-unit-input?'] = "False"
            else:
                can_add = RappiProductUtils.setProductAsIncompatible(products_dict)
                products_dict['k match-unit-input?'] = "False"

        return can_add

    @staticmethod
    def setMasterProductId(li_product, products_dict):
        a_tag = li_product.find("a")
        if a_tag is not None:
            href = a_tag.get("href")
            if href is not None:
                if href.rfind("/p/") != -1:
                    splited_href = href.split('-')
                    products_dict['master-product-id'] = splited_href[len(splited_href) - 1]
                elif "produto/" in href:
                    splited_href = href.split('produto/')[1]
                    products_dict['master-product-id'] = splited_href.split("_")[1]                  

        if "master-product-id" not in products_dict:
            products_dict['master-product-id'] = "-"

    @staticmethod
    def updateProduct(li_product, products_dict, term, unit, keywords):
        can_add = True

        # set product_id
        products_dict['product-id'] = li_product.get("data-qa").split("_")[1]
        # set master_product_id
        RappiProductUtils.setMasterProductId(li_product, products_dict)
            
        # set product_price
        product_price = RappiProductUtils.getProductPrice(li_product)
        products_dict['product-price'] = product_price
        # set product_real_price
        products_dict['product-real-price'] = RappiProductUtils.getProductRealPrice(li_product, product_price)
        # set product_unit
        can_add = RappiProductUtils.setProductUnit(li_product, products_dict, product_price, unit)

        if can_add:
            # set product_name
            can_add = RappiProductUtils.setProductName(li_product, products_dict, keywords, term)

        return can_add

    @staticmethod
    def getProductList(response:requests.models.Response, term:str, store_id:str, store_type:str, unit:str, keywords:tuple, original_queries_dic:dict)->list:
        products_dict = {}
        products_list = []
        soup = BeautifulSoup(response.content, "html.parser")

        li_products_tags = soup.find_all("li", attrs= { "data-qa": re.compile("\Aproduct-item") })
        
        for li_product in li_products_tags:
            product_out_stock = RappiProductUtils.getProductOutStock(li_product)
            if InputSettings.ONLY_AVAILABLE_PRODUCTS and product_out_stock == 'True':
                continue
            
            products_dict = {}
            products_dict['k term']= original_queries_dic.get(term, term)
            products_dict['k unit-input']= unit
            products_dict['store-id'] = store_id
            products_dict['store-type'] = store_type
            can_add = RappiProductUtils.updateProduct(li_product, products_dict, term, unit, keywords)
            # set product_out_stock
            if can_add:
                products_dict['product-out-stock'] = product_out_stock
                products_list.append(products_dict)

        return products_list
    
    @staticmethod
    def getErrorDict(error, term, store, url):
        error_dict = {}
        error_dict['error'] = error
        error_dict['query'] = term
        error_dict['store'] = store
        error_dict['url'] = url

        return error_dict

    @staticmethod
    def scrapeProducts(store:str, term:str, unit:str, keywords:tuple, original_queries_dic:dict)->tuple:
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
            term = term.replace('%20',' ')

            if response.status_code == 200:
                products_list = RappiProductUtils.getProductList(response, term, store_id, store_type, unit, keywords, original_queries_dic)
                error_dict = RappiProductUtils.getErrorDict("", "", "", "")
            else:
                print(f"\rERROR: {response.status_code}")
                error_dict = RappiProductUtils.getErrorDict(response.status_code, term, store, url)
        except requests.exceptions.HTTPError as err:
            if response.status_code == 429:
                print(f'\rTOO MANY PRODUCTS REQUESTS: WAIT 60s')
                time.sleep(60)
                try:
                    response = requests.get(url, headers=request_heather)
                    response.raise_for_status()
                    if response.status_code == 200:
                        products_list = RappiProductUtils.getProductList(response, term, store_id, store_type, unit, keywords, original_queries_dic)
                        error_dict = RappiProductUtils.getErrorDict("", "", "", "")
                    else:
                        print(f"\rERROR: {response.status_code}")
                        error_dict = RappiProductUtils.getErrorDict(response.status_code, term, store, url)
                except requests.exceptions.RequestException as err:
                    err = str(err)
                    error_dict = RappiProductUtils.getErrorDict(err, term, store, url)
            elif response.status_code == 502:
                print(f'\rBAD GATEWAY: LETS TRY AGAIN IN 30s')
                time.sleep(30)
                try:
                    response = requests.get(url, headers=request_heather)
                    response.raise_for_status()
                    if response.status_code == 200:
                        products_list = RappiProductUtils.getProductList(response, term, store_id, store_type, unit, keywords, original_queries_dic)
                        error_dict = RappiProductUtils.getErrorDict("", "", "", "")
                    else:
                        print(f"\rERROR: {response.status_code}")
                        error_dict = RappiProductUtils.getErrorDict(response.status_code, term, store, url)
                except requests.exceptions.RequestException as err:
                    err = str(err)
                    error_dict = RappiProductUtils.getErrorDict(err, term, store, url)
            else:
                print(f"\rERROR: {response.status_code}")
                error_dict = RappiProductUtils.getErrorDict(response.status_code, term, store, url)
        except requests.exceptions.RequestException as err:
            err = str(err)
            print(f"\rAn error occurred during the request: {err}")
            error_dict = RappiProductUtils.getErrorDict(err, term, store, url)
        
        error_list.append(error_dict)
        return products_list, error_list
    
    @staticmethod
    def setupProductObjectWithHeader(product: dict):
        headers_products = InputSettings.EXCEL_HEADER

        if list(product.keys()) != headers_products:
            _product = {}
            
            for header_col in headers_products:
                if header_col not in product.keys():
                    _product[header_col] = '-'
                else:
                    _product[header_col] = product[header_col]
            return _product
        else:
            return product
