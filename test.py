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
        print(json_data)
except Exception as err:
    print(err)
     