import requests
 
API_KEY = "339f2d300f51462e9f7508a2e0f3f518"
 
headers = {
    "x-api-key": API_KEY
}
 
url = "https://api.nationaltransport.ie/gtfsr/v2/vehicles"
 
response = requests.get(url, headers=headers)
 
print(response.status_code)
print(response. text)
