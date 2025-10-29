# https://getmodsapk.com/search?query=JioSaavn
# requires: pip install requests
import requests
import urllib.parse
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("google_api")
CSE_ID  = "342d7ccd8c8d043c2"  # create a CSE that searches the whole web (sites to search = "www.google.com") or restrict to trusted sites

query   = "Jio Hotstar Mod"

url = "https://www.googleapis.com/customsearch/v1"
params = {
    "key": API_KEY,
    "cx": CSE_ID,
    "q": query,
    "num": 10,   # max per request is 10
    "start": 20
}

resp = requests.get(url, params=params)
resp.raise_for_status()
data = resp.json()
for i, item in enumerate(data.get("items", []), start=1):
    print(i, item.get("title"))
    print("  ", item.get("link"))
    print()
