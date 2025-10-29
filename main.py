import json
import pandas as pd
from tkinter import Tk, filedialog
import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()
token  = os.getenv("GITHUB_TOKEN")
API_KEY = os.getenv("google_api")
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

    df_github = pd.DataFrame(all_github_rows)
    df_google = pd.DataFrame(all_google_rows)

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_github.to_excel(writer, index=False, sheet_name="Github")
        df_google.to_excel(writer, index=False, sheet_name="Mod apps")

    print("✅ Excel file created successfully!")

if __name__ == "__main__":
    main()
