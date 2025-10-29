import requests
import json
import time
import os


QUERIES = ["Mukesh Ambani AI", "Mukesh Ambani", "Ambani"]  # <-- your list of queries

def fetch_data(endpoint, query):
    url = f"https://facebook-scraper3.p.rapidapi.com/search/{endpoint}"
    headers = {
        "x-rapidapi-host": "facebook-scraper3.p.rapidapi.com",
        "x-rapidapi-key": API_KEY
    }
    params = {"query": query}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Always extract only 'results' if present
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        elif isinstance(data, list):
            return data
        else:
            print(f"⚠️ Unexpected response for {endpoint} → {query}: {data}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {endpoint} for '{query}':", e)
        return []


def main():
    all_videos, all_posts, all_pages = [], [], []

    for query in QUERIES:
        print(f"\n🔍 Fetching for query: {query}")

        all_videos.extend(fetch_data("videos", query))
        all_posts.extend(fetch_data("posts", query))
        all_pages.extend(fetch_data("pages", query))

        time.sleep(1)  # to respect rate limits

    # Save combined results
    with open("videos_all.json", "w", encoding="utf-8") as f:
        json.dump(all_videos, f, ensure_ascii=False, indent=4)

    with open("posts_all.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=4)

    with open("pages_all.json", "w", encoding="utf-8") as f:
        json.dump(all_pages, f, ensure_ascii=False, indent=4)

    print("\n🎉 Done! Saved:")
    print("📁 videos_all.json")
    print("📁 posts_all.json")
    print("📁 pages_all.json")


if __name__ == "__main__":
    main()