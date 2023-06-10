import json
import requests
import time
from urllib.request import HTTPError

def aisles(path,store_id):
    aisles_list=[]
    url = f"https://www.rappi.com.br/_next/data/{path}/pt-BR/ssg/{store_id}"
    aisle_url = f'{url}.json'
    request_heather = {'referer':f'https://www.rappi.com.br/lojas/{store_id}/catalogo'}
    response = requests.get(aisle_url, headers=request_heather)

    if response.status_code == 429:
        print('TOO MANY PRODUCTS REQUESTS: WAIT 30s')
        time.sleep(30)
        response = requests.get(aisle_url, headers=request_heather)
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

def sub_aisles(path, store_id, aisle):
    sub_aisles_list=[]
    url = f'https://www.rappi.com.br/_next/data/{path}/pt-BR/ssg/{store_id}/{aisle}'
    sub_aisle_url = f"{url}.json"
    request_heather = {'referer':f'https://www.rappi.com.br/lojas/{store_id}/catalogo'}
    response = requests.get(sub_aisle_url, headers=request_heather)

    if response.status_code == 429:
        print('TOO MANY PRODUCTS REQUESTS: WAIT 30s')
        time.sleep(30)
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
    
    aisles_dict[aisle] = sub_aisles_list
    return  aisles_dict

aisles_dict={}
products_list = []

store_id = '900027422-verdemar'
path = 'jc4CmuS9qVEJg_6HsbdRk'

aisles_list = aisles(path,store_id)

for aisle in aisles_list:
    sub_aisles_list = sub_aisles(path,store_id,aisle)

print(f'AISLE_DICT: {aisles_dict}')

for key in aisles_dict:
    values = aisles_dict[key]
    first_value = values[0]
    for value in values:
        url = f"https://www.rappi.com.br/_next/data/{path}/pt-BR/ssg/{store_id}/{key}/{value}.json"
        request_heather = {'referer':f'https://www.rappi.com.br/lojas/{store_id}/{key}/{first_value}'}
        response = requests.get(url, headers=request_heather)
        if response.status_code == 429:
            print('TOO MANY PRODUCTS REQUESTS: WAIT 30s')
            time.sleep(30)
            response = requests.get(url, headers=request_heather)
            json_data = response.json()
        elif response.status_code == 502:
            print('BAD GATEWAY: WAIT 1m')
            time.sleep(60)
            response = requests.get(url, headers=request_heather)
            json_data = response.json()
        else:
            json_data = response.json()

        pageProps = json_data['pageProps']
        fallback = pageProps['fallback']
        storefront = fallback[f'storefront/{store_id}/{key}/{value}']
        aisle_detail_response = storefront['aisle_detail_response']
        data = aisle_detail_response['data']
        components = data['components']

        for component in components:
            resource = component['resource']
            products = resource['products']
            for product in products:
                products_list.append(product)

    print(f'{key} PRODUCTS SCRAPED:{len(products_list)}')
        
print(f'TOTAL PRODUCTS:{len(products_list)}')

# print(len(urls_list))
# print(urls_list[0]) 





