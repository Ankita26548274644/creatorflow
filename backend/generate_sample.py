"""
Generates a synthetic valid CSV with 150 rows for testing the validation endpoint.
Run from backend/ directory: python generate_sample.py
"""
import random
import csv
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

rows = []
start = datetime(2024, 1, 1)
captions = [
    "Morning motivation post",
    "Quick tip of the day",
    "Behind the scenes",
    "Weekend vibes",
    "Answering your questions",
    "New content drop",
    "Sunset photo dump",
    "Throwback Thursday",
    "Weekly recap",
    "Product update",
]

for i in range(1, 151):
    date = start + timedelta(days=i)
    likes = random.randint(20, 800)
    impressions = likes * random.randint(4, 15)  # always greater than likes
    comments = random.randint(1, 80)
    shares = random.randint(0, 40)
    caption = random.choice(captions) + f" #{i}"
    rows.append([
        i,
        date.strftime("%Y-%m-%d"),
        caption,
        likes,
        comments,
        shares,
        impressions,
    ])

output_path = Path(__file__).resolve().parent.parent / "sample_data" / "valid_150.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "post_id", "date", "caption", "likes", "comments", "shares", "impressions"
    ])
    writer.writerows(rows)

print(f"Generated {output_path} with {len(rows)} rows.")