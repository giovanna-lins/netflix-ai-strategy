"""
Generates a short, member-tailored tagline -- and, on demand, a stylized
thumbnail -- per title using the Gemini API. Both fall back gracefully
(a template line, or no image at all) if there's no API key, no
internet, or any other error -- the app must always run.
"""
import os
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = "gemini-2.5-flash"
IMAGE_MODEL = "gemini-2.5-flash-image"


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
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            max_output_tokens=40,
        )
        response = client.models.generate_content(model=MODEL, contents=prompt, config=config)
        text = (response.text or "").strip().strip('"')
        # Guard against any stray long/multi-line output slipping through.
        if not text or len(text) > 150 or "\n" in text:
            return template_tagline(title_row, member)
        return text
    except Exception:
        return template_tagline(title_row, member)


def generate_thumbnail(title_row: pd.Series, member: pd.Series) -> Optional[bytes]:
    """
    Generates one abstract, mood-and-color thumbnail for a title, styled
    for the member's taste. Deliberately avoids photorealism, recognizable
    faces/characters, logos, or text in the image -- this keeps it a
    stylized illustration rather than something that could look like a
    real movie poster (brand/IP risk). Returns PNG bytes, or None if
    there's no key or anything goes wrong -- the colored card is always
    the fallback.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        client = genai.Client(api_key=api_key)
        genre = title_row["genres"].split("|")[0]
        prompt = (
            f"An abstract, stylized illustration for a streaming app thumbnail. "
            f"Mood and color palette should evoke the genre '{genre}' "
            f"(full genres: {title_row['genres']}), for a viewer who enjoys "
            f"{member['favorite_genres']}. Abstract shapes, gradients, and symbolic "
            f"imagery only -- no text, no logos, no recognizable faces, no real actors "
            f"or characters, no photorealism. Square composition."
        )
        response = client.models.generate_content(model=IMAGE_MODEL, contents=prompt)
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return part.inline_data.data
        return None
    except Exception:
        return None
