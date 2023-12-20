import requests

url = "https://gateway.dubailand.gov.ae/open-data/transactions"

payload = "{\"P_FROM_DATE\":\"01/01/2023\",\"P_TO_DATE\":\"12/20/2023\",\"P_GROUP_ID\":\"\",\"P_IS_OFFPLAN\":\"\",\"P_IS_FREE_HOLD\":\"\",\"P_AREA_ID\":\"\",\"P_USAGE_ID\":\"\",\"P_PROP_TYPE_ID\":\"\",\"P_TAKE\":\"10000\",\"P_SKIP\":\"0\",\"P_SORT\":\"TRANSACTION_NUMBER_ASC\"}"
headers = {
  'Accept': 'application/json, */*',
  'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
  'AppUser': '',
  'Connection': 'keep-alive',
  'Content-Type': 'application/json; charset=UTF-8',
  'Origin': 'https://dubailand.gov.ae',
  'Referer': 'https://dubailand.gov.ae/',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-site',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'consumer-id': 'gkb3WvEG0rY9eilwXC0P2pTz8UzvLj9F',
  'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text.encode('utf-8'))
