"""
One-time generator for CineMatch's synthetic data.
Run once: python generate_data.py
Writes members.csv, catalog.csv, availability.csv, policy.txt into /data.

All members and titles are fictional. Ratings order (low -> high):
G < PG < PG-13 < R
"""
import os
import csv

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

TERRITORIES = ["BR", "IN", "JP", "MX", "US", "AE"]

MEMBERS = [
    # id,   name,            segment,             territory, genres (favorite),   maturity_ceiling
    ("M1", "Ana Souza",      "Bingers",            "BR", "Thriller|Drama",     "R"),
    ("M2", "Marco Silva",    "Casual Viewers",     "BR", "Action|Comedy",      "PG-13"),
    ("M3", "Priya Nair",     "Romantics",          "IN", "Romance|Drama",      "PG-13"),
    ("M4", "Chen Wei",       "Sci-Fi Explorers",   "JP", "Sci-Fi|Action",      "R"),
    ("M5", "Sofia Reyes",    "Family Time",        "MX", "Family|Animation",   "PG"),
    ("M6", "Liam Cole",      "Thrill Seekers",     "US", "Horror|Thriller",    "R"),
    ("M7", "Noor Al-Farsi",  "Culture Seekers",    "AE", "Documentary|Drama",  "PG-13"),
    ("M8", "Yuki Tanaka",    "Anime Fans",         "JP", "Anime|Fantasy",      "PG-13"),
]

# id,   title,                 genres,                  rating, popularity, color
CATALOG = [
    ("T1",  "Crimson Ledger",       "Thriller|Drama",        "R",     78, "#8B0000"),
    ("T2",  "Silver Static",        "Thriller|Drama",        "PG-13", 65, "#4B4B4B"),
    ("T3",  "Midnight Currency",    "Thriller|Crime",        "R",     70, "#2F2F4F"),
    ("T4",  "Last Ferry Out",       "Drama",                 "PG-13", 55, "#5C4033"),
    ("T5",  "Harborlight",          "Drama|Romance",         "PG",    48, "#6A5ACD"),
    ("T6",  "Payload Protocol",     "Action|Comedy",         "PG-13", 82, "#FF8C00"),
    ("T7",  "Getaway Deluxe",       "Comedy|Action",         "PG-13", 74, "#FFA500"),
    ("T8",  "Neon Skyline",         "Action|Sci-Fi",         "R",     88, "#00CED1"),
    ("T9",  "Backfire",             "Action",                "PG-13", 60, "#B22222"),
    ("T10", "Two Left Feet",        "Comedy",                "PG",    52, "#FFD700"),
    ("T11", "Paper Moonlight",      "Romance|Drama",         "PG-13", 85, "#C71585"),
    ("T12", "Second Bloom",         "Romance",                "PG",   58, "#FF69B4"),
    ("T13", "Letters Unsent",       "Romance|Drama",         "PG",    44, "#DB7093"),
    ("T14", "Ion Drift",            "Sci-Fi|Action",         "PG-13", 91, "#00BFFF"),
    ("T15", "Gravity Well",         "Sci-Fi",                "PG-13", 67, "#1E90FF"),
    ("T16", "Colony Nine",          "Sci-Fi|Drama",          "R",     73, "#4682B4"),
    ("T17", "Bramblewood",          "Family|Animation",      "G",     80, "#32CD32"),
    ("T18", "The Kite Keeper",      "Family|Animation",      "PG",    76, "#228B22"),
    ("T19", "Sunny Side Studios",   "Family|Comedy",         "G",     62, "#ADFF2F"),
    ("T20", "Nightshade Manor",     "Horror|Thriller",       "R",     84, "#4B0082"),
    ("T21", "The Hollow Choir",     "Horror",                "R",     71, "#301934"),
    ("T22", "Static at Dusk",       "Horror|Thriller",       "PG-13", 56, "#483D8B"),
    ("T23", "Concrete Rivers",      "Documentary",           "PG-13", 40, "#708090"),
    ("T24", "The Last Harvest",     "Documentary|Drama",     "PG",    36, "#556B2F"),
    ("T25", "Quiet Static",         "Documentary|Drama",     "PG-13",  8, "#778899"),
    ("T26", "Iron Bloom Legacy",    "Anime|Fantasy",         "PG-13", 87, "#9932CC"),
    ("T27", "Paper Cranes",         "Anime|Fantasy",         "PG-13", 75, "#BA55D3"),
    ("T28", "Skyforge Chronicles",  "Fantasy|Action",        "PG-13", 69, "#8A2BE2"),
    ("T29", "Red Room Diaries",     "Thriller|Exploitation", "R",     80, "#800000"),
    ("T30", "Glasshouse Rules",     "Drama|Crime",           "R",     63, "#2E2E2E"),
    ("T31", "The Understudy",       "Drama|Comedy",          "PG-13", 50, "#DAA520"),
    ("T32", "Wildfire Season",      "Action|Drama",          "R",     77, "#B8860B"),
    ("T33", "Wonderland Overtime",  "Family|Animation",      "PG-13", 70, "#DA70D6"),
]

# Exceptions to the "available everywhere, rights window open" default.
# (title_id, territory) -> (available, rights_window_ok)
AVAILABILITY_EXCEPTIONS = {
    ("T11", "IN"): (False, True),   # Paper Moonlight: not licensed in India
    ("T27", "JP"): (True, False),   # Paper Cranes: licensed in Japan, but rights window has closed
    ("T8", "JP"):  (False, True),   # Neon Skyline: not available in Japan
}

POLICY_TEXT = """CineMatch Editorial & Brand Policy (v1)
This is a short, local policy file used for a simple keyword lookup
(a stand-in for full semantic retrieval over a real policy corpus).

1. Titles tagged with the genre "Exploitation" must be flagged for editorial review, not served automatically.

2. Titles with a popularity score below 15 are considered low-confidence and must be flagged for editorial review.

3. All other titles that pass availability and maturity-rating checks may be served automatically without further review.
"""


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(os.path.join(DATA_DIR, "members.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "segment", "territory", "favorite_genres", "maturity_ceiling"])
        w.writerows(MEMBERS)

    with open(os.path.join(DATA_DIR, "catalog.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "title", "genres", "maturity_rating", "popularity", "color"])
        w.writerows(CATALOG)

    with open(os.path.join(DATA_DIR, "availability.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["title_id", "territory", "available", "rights_window_ok"])
        for title in CATALOG:
            title_id = title[0]
            for territory in TERRITORIES:
                available, rights_window_ok = AVAILABILITY_EXCEPTIONS.get(
                    (title_id, territory), (True, True)
                )
                w.writerow([title_id, territory, available, rights_window_ok])

    with open(os.path.join(DATA_DIR, "policy.txt"), "w") as f:
        f.write(POLICY_TEXT)

    print(f"Wrote members.csv ({len(MEMBERS)} members), catalog.csv ({len(CATALOG)} titles), "
          f"availability.csv ({len(CATALOG) * len(TERRITORIES)} rows), and policy.txt to {DATA_DIR}")


if __name__ == "__main__":
    main()
