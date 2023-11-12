import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    # 'Accept-Encoding': 'gzip, deflate, br',
    "x-api-key": "zcXG3YV70a2u7T9tTK9S7MFMJUUZ66Vawq5qXxnj",
    "Content-Type": "application/json",
    "Origin": "https://www.supercuts.com",
    "Connection": "keep-alive",
    "Referer": "https://www.supercuts.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

json_data = {
    "salonId": "82435",
    "siteId": "1",
}

response = requests.post(
    "https://api-booking.regiscorp.com/v1/getsalondetails",
    headers=headers,
    json=json_data,
)
print(response.text)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
# data = '{"salonId":"82435","siteId":"1"}'
# response = requests.post('https://api-booking.regiscorp.com/v1/getsalondetails', headers=headers, data=data)
