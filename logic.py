"""
Core, transparent (non-AI) logic for CineMatch:
loading data, ranking titles, and (in later phases) grounding checks and feedback.
"""
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_members() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "members.csv"))


def load_catalog() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "catalog.csv"))


def load_availability() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "availability.csv"))


def load_policy_text() -> str:
    with open(os.path.join(DATA_DIR, "policy.txt")) as f:
        return f.read()


# Segment-level genre preferences (distinct from a member's own stated
# favorite genres) -- models "people like this tend to enjoy these too".
SEGMENT_GENRE_AFFINITY = {
    "Bingers": {"Thriller", "Drama", "Crime"},
    "Casual Viewers": {"Comedy", "Action", "Family"},
    "Romantics": {"Romance", "Drama"},
    "Sci-Fi Explorers": {"Sci-Fi", "Action", "Fantasy"},
    "Family Time": {"Family", "Animation", "Comedy"},
    "Thrill Seekers": {"Horror", "Thriller", "Action"},
    "Culture Seekers": {"Documentary", "Drama"},
    "Anime Fans": {"Anime", "Fantasy", "Sci-Fi"},
}

DEFAULT_WEIGHTS = {"genre": 5, "segment": 3, "popularity": 2}


def rank_titles(member: pd.Series, catalog: pd.DataFrame, weights: dict = None) -> pd.DataFrame:
    """
    Score every title for one member using a transparent, explainable formula:
        score = genre_weight * genre_match_count
              + segment_weight * segment_affinity_count
              + popularity_weight * (popularity / 100)
    Returns the catalog sorted by score, descending, with the score
    components attached so the reasoning can be shown on screen.
    """
    weights = weights or DEFAULT_WEIGHTS
    favorite_genres = set(member["favorite_genres"].split("|"))
    segment_genres = SEGMENT_GENRE_AFFINITY.get(member["segment"], set())

    df = catalog.copy()
    title_genre_sets = df["genres"].apply(lambda g: set(g.split("|")))

    df["genre_match"] = title_genre_sets.apply(lambda g: len(g & favorite_genres))
    df["segment_affinity"] = title_genre_sets.apply(lambda g: len(g & segment_genres))
    df["score"] = (
        weights["genre"] * df["genre_match"]
        + weights["segment"] * df["segment_affinity"]
        + weights["popularity"] * (df["popularity"] / 100)
    ).round(2)

    return df.sort_values("score", ascending=False).reset_index(drop=True)
