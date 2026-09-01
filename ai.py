"""
Generates a short, member-tailored tagline per title using the Gemini API.
Falls back to a plain template if there's no API key, no internet, or
any other error -- the app must always run.
"""
import os

import pandas as pd
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-2.5-flash"


def template_tagline(title_row: pd.Series, member: pd.Series) -> str:
    genre = title_row["genres"].split("|")[0].lower()
    return f"A {genre} pick made for {member['segment'].lower()} fans like {member['name'].split()[0]}."


def generate_tagline(title_row: pd.Series, member: pd.Series) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return template_tagline(title_row, member)

    try:
        client = genai.Client(api_key=api_key)
        prompt = (
            f"Write one short, upbeat streaming-app tagline (max 12 words) for the title "
            f"'{title_row['title']}' (genres: {title_row['genres']}), tailored to a "
            f"'{member['segment']}' viewer who enjoys {member['favorite_genres']}. "
            f"Respond with only the tagline text, no quotes, no explanation."
        )
        response = client.models.generate_content(model=MODEL, contents=prompt)
        text = (response.text or "").strip().strip('"')
        return text if text else template_tagline(title_row, member)
    except Exception:
        return template_tagline(title_row, member)
