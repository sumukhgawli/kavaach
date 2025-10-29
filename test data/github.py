import requests
import urllib.parse
from dotenv import load_dotenv
import os

load_dotenv()
token  = os.getenv("GITHUB_TOKEN")

query = "JioSaavn" 

encoded_query = urllib.parse.quote(query)

url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&order=desc"

headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {token}"  
}

response = requests.get(url, headers=headers)
data = response.json()
if response.status_code != 200:
    print(f"❌ Error {response.status_code}: {data.get('message')}")
else:
    print(f"✅ API call successful. Remaining requests: {response.headers.get('X-RateLimit-Remaining')}")
    print("-" * 80)

    # 🔁 Loop through and print each repo's info
    for idx, item in enumerate(data.get("items", []), start=1):
        print(f"📦 Repo #{idx}")
        print(f"   Name: {item['name']}")
        print(f"   Full Name: {item['full_name']}")
        print(f"   Owner: {item['owner']['login']}")
        print(f"   Language: {item.get('language')}")
        print(f"   Stars: {item['stargazers_count']}")
        print(f"   Forks: {item['forks_count']}")
        print(f"   URL: {item['html_url']}")
        print(f"   Description: {item.get('description')}")
        print(f"   Created At: {item['created_at']}")
        print(f"   Updated At: {item['updated_at']}")
        print("-" * 80)

print(f"Status: {response.status_code}")
print(f"Remaining requests: {response.headers.get('X-RateLimit-Remaining')}")
print(f"Total results: {data.get('total_count')}")
