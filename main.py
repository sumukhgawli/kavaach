import json
import pandas as pd
from tkinter import Tk, filedialog
import os
import requests
import urllib.parse
from dotenv import load_dotenv
import time

load_dotenv()
token  = os.getenv("GITHUB_TOKEN")
API_KEY = os.getenv("google_api")
print("API_KEY:", API_KEY)
facebook_api = os.getenv("facebook_api")
CSE_ID  = "342d7ccd8c8d043c2" 

def github_data(query):
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&order=desc"

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {data.get('message')}")
            return {"error": data.get("message", "Unknown error"), "status": response.status_code}

        print(f"✅ API call successful. Remaining requests: {response.headers.get('X-RateLimit-Remaining')}")
        return data  # ✅ Return the full JSON data for further use

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Network Error: {e}")
        return {"error": str(e), "status": "network_error"}

def mod_data(query,total_results):
    url = "https://www.googleapis.com/customsearch/v1"
    all_items = []
    start = 0
    try:
        for start in range(start, total_results + 1, 10):  # API returns max 10 per call
            params = {
                "key": API_KEY,
                "cx": CSE_ID,
                "q": query,
                "num": 10,
                "start": start
            }

            resp = requests.get(url, params=params)
            data = resp.json()

            if resp.status_code != 200:
                print(f"❌ Google error {resp.status_code}: {data.get('error', {}).get('message')}")
                break

            items = data.get("items", [])
            if not items:
                break

            all_items.extend(items)
            print(f"✅ Google: {query} — fetched {len(items)} (total so far: {len(all_items)})")

            if len(items) < 10:
                break  # no more pages

        return {"items": all_items}

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Network error while calling Google API: {e}")
        return {"error": str(e), "status": "network_error"}

def facebook_data(query):
    headers = {
        "x-rapidapi-host": "facebook-scraper3.p.rapidapi.com",
        "x-rapidapi-key": facebook_api   # make sure this is defined globally or passed in
    }

    endpoints = ['videos', 'posts', 'pages']
    all_data = {}

    for endpoint in endpoints:
        url = f"https://facebook-scraper3.p.rapidapi.com/search/{endpoint}"
        params = {"query": query}

        try:
            print(f"🔍 Fetching {endpoint} for '{query}'...")
            response = requests.get(url, headers=headers, params=params)

            # Handle rate limit errors
            if response.status_code == 429:
                print(f"⚠️ Rate limited on {endpoint}, waiting 10 seconds...")
                time.sleep(10)
                response = requests.get(url, headers=headers, params=params)

            response.raise_for_status()
            data = response.json()

            # Ensure we get only actual results
            items = data.get("results")
            if items and isinstance(items, list):
                all_data[endpoint] = items
                print(f"✅ Got {len(items)} {endpoint}")
            else:
                all_data[endpoint] = []
                print(f"⚠️ No {endpoint} results found")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching {endpoint} for '{query}': {e}")
            all_data[endpoint] = []

    return all_data
def main():
    root = Tk()
    root.withdraw()

    print("📂 Please select the folder where the Excel file will be saved...")

    folder_path = filedialog.askdirectory(title="Select Save Folder")

    if not folder_path:
        print("❌ No folder selected. Exiting.")
        return

    output_path = os.path.join(folder_path, "combined_output.xlsx")

    print(f"💾 Saving file to: {output_path}")

    github_queries = ["JioSaavn", "JioTv", "JioMart"]
    google_queries = ["Jio Hotstar Mod", "jiotv+ mod"]
    facebook_queries = ["Mukesh Ambani", "Ambani", "Mukesh Ambani AI"]


    all_github_rows = []
    all_google_rows = []

    for q in github_queries:
        print(f"\n🔍 [GitHub] Fetching data for: {q}")
        data1 = github_data(q)

        for item in data1.get("items", []):
            all_github_rows.append({
                "Query": q,
                "Name": item["name"],
                "Full Name": item["full_name"],
                "Owner": item["owner"]["login"],
                "Language": item.get("language"),
                "Stars": item["stargazers_count"],
                "Forks": item["forks_count"],
                "URL": item["html_url"],
                "Description": item.get("description"),
                "Created At": item["created_at"],
                "Updated At": item["updated_at"]
            })

    for q in google_queries:
        print(f"\n🔍 [Google] Fetching data for: {q}")
        data2 = mod_data(q, total_results=20)

        for item in data2.get("items", []):
            all_google_rows.append({
                "Query": q,
                "Title": item.get("title"),
                "Link": item.get("link")
            })

    all_facebook_rows = []

    for q in facebook_queries:
        print(f"\n🔍 [Facebook] Fetching data for: {q}")
        data3 = facebook_data(q)

        # Loop through each endpoint (videos, posts, pages)
        for endpoint, items in data3.items():
            for item in items:
                # Determine fields safely
                fb_type = item.get("type")
                url = (
                    item.get("url")
                    or item.get("video_url")
                    or (item.get("profile_url") if fb_type == "page" else None)
                )

                # Extract author info
                if fb_type == "page":
                    author_name = item.get("name")
                    profile_url = item.get("profile_url")
                elif fb_type == "post":
                    author_name = item.get("author", {}).get("name") if isinstance(item.get("author"), dict) else None
                    profile_url = item.get("author", {}).get("url") if isinstance(item.get("author"), dict) else None
                elif fb_type in ["video", "search_video"]:
                    author_name = item.get("author", {}).get("name") if isinstance(item.get("author"), dict) else None
                    profile_url = item.get("author", {}).get("url") if isinstance(item.get("author"), dict) else None
                else:
                    author_name = None
                    profile_url = None

                # Only add valid entries
                if url and author_name:
                    all_facebook_rows.append({
                        "Query": q,
                        "Type": fb_type,
                        "Author": author_name,
                        "Profile_URL": profile_url,
                        "URL": url
                    })
    df_github = pd.DataFrame(all_github_rows)
    df_google = pd.DataFrame(all_google_rows)
    df_facebook = pd.DataFrame(all_facebook_rows)
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_github.to_excel(writer, index=False, sheet_name="Github")
        df_google.to_excel(writer, index=False, sheet_name="Mod apps")
        df_facebook.to_excel(writer, index=False, sheet_name="Facebook")
    print("✅ Excel file created successfully!")

if __name__ == "__main__":
    main()
