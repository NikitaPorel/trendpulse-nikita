import requests
import time
import json
import os
from datetime import datetime

#Making the API calls
TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

headers = {
    "User-Agent": "TrendPulse/1.0"
}

#Keywords used to classify stories
categories = {
    "technology": [
        "AI", "software", "tech", "code", "computer", "data", "cloud", "API", "GPU", "LLM"
    ],
    "worldnews": [
        "war", "government", "country", "president", "election", "climate", "attack", "global"
        ],
    "sports": [
        "NFL", "NBA", "FIFA", "sport", "game", "team", "player", "league", "championship"
    ],
    "science": [
        "research", "study", "space", "physics", "biology", "discover", "NASA", "genome"
    ],
    "entertainement": [
        "movie", "film", "music", "Netflix", "game", "book", "show", "award", "streaming"
    ]
}



#Get the first 500 top story IDs
try:
    response = requests.get(TOP_STORIES_URL, headers=headers, timeout=10)
    response.raise_for_status()

    story_ids = response.json()[:500]
    print(f"Fetched {len(story_ids)} story IDs.")

except requests.RequestException as error:
    print(f"Failed to fetch top stories: {error}")
    story_ids = []


#Fetch details of every story
stories = []
for story_id in story_ids:

    try:
        url = ITEM_URL.format(id=story_id)

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        story = response.json()

        if story and story.get("type") == "story" and story.get("title"):
            stories.append(story)

    except requests.RequestException as error:
        print(f"Failed to fetch story {story_id}: {error}")
        continue

print(f"Successfully fetched {len(stories)} stories.")



#Categorize stories
collected_stories = []

category_count = {
    category: 0 for category in categories
}

for category, keywords in categories.items():
    for story in stories:
        if category_count[category] >= 25:
            break

        title = story.get("title", "")
        title_lower = title.lower()

        matched = False

        for keyword in keywords:
            if keyword.lower() in title_lower:
                matched = True
                break

        if matched:
            already_collected = any(
                item["post_id"] == story.get("id")
                for item in collected_stories
            )

            if already_collected:
                continue

            collected_stories.append({
                "post_id": story.get("id"),
                "title": story.get("title"),
                "category": category,
                "score": story.get("score", 0),
                "num_comments": story.get("descendents", 0),
                "author": story.get("by", "unknown"),
                "collected_at": datetime.now().isoformat(),
            })

            category_count[category] += 1

    time.sleep(2)

    os.makedirs("data", exist_ok=True)

    date_string = datetime.now().strftime("%Y%m%d")

    file_path = f"data/trends_{date_string}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(collected_stories, file, indent=4, ensure_ascii=False)



print(f"Collected {len(collected_stories)} stories.")
print(f"Saved to {file_path}")
print("\nStories per category:")

for category, count in category_count.items():
    print(f"{category}: {count}")