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
FEEDBACK_WEIGHT = 1.5


def rank_titles(member: pd.Series, catalog: pd.DataFrame, weights: dict = None, feedback_bonus: dict = None) -> pd.DataFrame:
    """
    Score every title for one member using a transparent, explainable formula:
        score = genre_weight * genre_match_count
              + segment_weight * segment_affinity_count
              + popularity_weight * (popularity / 100)
              + FEEDBACK_WEIGHT * feedback_bonus_for_this_title's_genres
    `feedback_bonus` is a {genre: count} dict built from past clicks/plays
    this session -- this is the "bandit-lite" stand-in for reinforcement
    learning: no training, just a running nudge per genre.
    Returns the catalog sorted by score, descending, with the score
    components attached so the reasoning can be shown on screen.
    """
    weights = weights or DEFAULT_WEIGHTS
    feedback_bonus = feedback_bonus or {}
    favorite_genres = set(member["favorite_genres"].split("|"))
    segment_genres = SEGMENT_GENRE_AFFINITY.get(member["segment"], set())

    df = catalog.copy()
    title_genre_sets = df["genres"].apply(lambda g: set(g.split("|")))

    df["genre_match"] = title_genre_sets.apply(lambda g: len(g & favorite_genres))
    df["segment_affinity"] = title_genre_sets.apply(lambda g: len(g & segment_genres))
    df["feedback_nudge"] = title_genre_sets.apply(lambda g: sum(feedback_bonus.get(genre, 0) for genre in g))
    df["score"] = (
        weights["genre"] * df["genre_match"]
        + weights["segment"] * df["segment_affinity"]
        + weights["popularity"] * (df["popularity"] / 100)
        + FEEDBACK_WEIGHT * df["feedback_nudge"]
    ).round(2)

    return df.sort_values("score", ascending=False).reset_index(drop=True)


RATING_ORDER = {"G": 0, "PG": 1, "PG-13": 2, "R": 3}


def check_policy(title_row: pd.Series, policy_text: str) -> list:
    """
    Simple keyword lookup over the local policy text (a stand-in for
    semantic retrieval over a real policy corpus). Returns a list of
    plain-language reasons if the title trips a rule, else [].
    """
    import re

    reasons = []
    genres = set(title_row["genres"].split("|"))
    for line in policy_text.splitlines():
        lower = line.lower()
        if "flag" not in lower:
            continue
        for genre in genres:
            if genre.lower() in lower:
                clean_line = re.sub(r"^\d+\.\s*", "", line.strip())
                reasons.append(f"policy: {clean_line}")

    match = re.search(r"popularity score below (\d+)", policy_text, re.IGNORECASE)
    if match:
        threshold = int(match.group(1))
        if title_row["popularity"] < threshold:
            reasons.append(
                f"policy: popularity {title_row['popularity']} is below the {threshold}-point confidence threshold"
            )
    return reasons


def ground_title(title_row: pd.Series, member: pd.Series, availability: pd.DataFrame, policy_text: str):
    """
    Checks one title against territory availability, the rights window,
    the member's maturity ceiling, and policy keywords. Returns
    ("cleared" | "flagged", [reasons]).
    """
    reasons = []

    match = availability[
        (availability["title_id"] == title_row["id"]) & (availability["territory"] == member["territory"])
    ]
    if match.empty or not bool(match.iloc[0]["available"]):
        reasons.append(f"not available in {member['territory']}")
    elif not bool(match.iloc[0]["rights_window_ok"]):
        reasons.append(f"rights window closed in {member['territory']}")

    if RATING_ORDER[title_row["maturity_rating"]] > RATING_ORDER[member["maturity_ceiling"]]:
        reasons.append(
            f"rated {title_row['maturity_rating']}, above this member's {member['maturity_ceiling']} ceiling"
        )

    reasons.extend(check_policy(title_row, policy_text))

    status = "flagged" if reasons else "cleared"
    return status, reasons
