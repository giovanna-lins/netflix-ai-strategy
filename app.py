import os

import streamlit as st
from dotenv import load_dotenv

import ai
import logic

load_dotenv()

st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")

st.title("🎬 CineMatch")
st.caption("Grounded personalized discovery — classroom MVP")

if os.environ.get("GEMINI_API_KEY") and os.environ.get("GEMINI_API_KEY") != "your-key-here":
    st.caption("🟢 Taglines generated live by Gemini")
else:
    st.caption("⚪ No GEMINI_API_KEY found — using template taglines (set one in .env to enable live AI copy)")

with st.expander("ℹ️ How this screen works (data → decision → feedback)"):
    st.markdown(
        "**DATA** (member + catalog + availability + policy) → "
        "**RANK** (score titles for this member) → "
        "**COMPOSE** (pick the top cleared titles) → "
        "**GENERATE** (AI writes each tagline) → "
        "**GROUND** (check territory, rating, policy — clear or flag) → "
        "**SERVE** (show cleared titles; flagged ones go to Needs review) → "
        "**FEEDBACK** (a Play click nudges future ranking, looping back to RANK)."
    )


if "tagline_cache" not in st.session_state:
    st.session_state.tagline_cache = {}
if "thumbnail_cache" not in st.session_state:
    st.session_state.thumbnail_cache = {}  # (title_id, member_id) -> PNG bytes
if "feedback" not in st.session_state:
    st.session_state.feedback = {}  # member_id -> {genre: nudge_count}
if "play_log" not in st.session_state:
    st.session_state.play_log = []  # list of {member, title}


def log_play(member_row, title_row):
    member_feedback = st.session_state.feedback.setdefault(member_row["id"], {})
    for genre in title_row["genres"].split("|"):
        member_feedback[genre] = member_feedback.get(genre, 0) + 1
    st.session_state.play_log.insert(0, {"member": member_row["name"], "title": title_row["title"]})


def get_tagline_cached(title_row, member_row) -> str:
    cache_key = (title_row["id"], member_row["id"])
    if cache_key not in st.session_state.tagline_cache:
        st.session_state.tagline_cache[cache_key] = ai.generate_tagline(title_row, member_row)
    return st.session_state.tagline_cache[cache_key]

members = logic.load_members()

member_labels = [
    f"{row['name']} — {row['segment']} ({row['territory']})"
    for _, row in members.iterrows()
]
selected_label = st.selectbox("Choose a member", member_labels)
selected_member = members.iloc[member_labels.index(selected_label)]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Segment", selected_member["segment"])
col2.metric("Territory", selected_member["territory"])
col3.metric("Favorite genres", selected_member["favorite_genres"])
col4.metric("Maturity ceiling", selected_member["maturity_ceiling"])

with st.expander("⚖️ Ranking weights (tweak the formula)"):
    w1, w2, w3 = st.columns(3)
    genre_w = w1.slider("Genre match", 0, 10, logic.DEFAULT_WEIGHTS["genre"])
    segment_w = w2.slider("Segment affinity", 0, 10, logic.DEFAULT_WEIGHTS["segment"])
    pop_w = w3.slider("Popularity", 0, 10, logic.DEFAULT_WEIGHTS["popularity"])
    st.caption("score = genre_weight × genre_match + segment_weight × segment_affinity + popularity_weight × (popularity / 100)")

weights = {"genre": genre_w, "segment": segment_w, "popularity": pop_w}
catalog = logic.load_catalog()
availability = logic.load_availability()
policy_text = logic.load_policy_text()
feedback_bonus = st.session_state.feedback.get(selected_member["id"], {})
ranked = logic.rank_titles(selected_member, catalog, weights, feedback_bonus)

TOP_N = 6
CANDIDATE_POOL = 12  # how far down the ranked list we look before giving up

cleared, flagged = [], []
for _, title in ranked.head(CANDIDATE_POOL).iterrows():
    status, reasons = logic.ground_title(title, selected_member, availability, policy_text)
    (cleared if status == "cleared" else flagged).append((title, reasons))
cleared = cleared[:TOP_N]
flagged = flagged[:4]


def render_card(col, title, status, reasons):
    with col:
        tagline = get_tagline_cached(title, selected_member) if status == "cleared" else None
        thumb_key = (title["id"], selected_member["id"])
        thumbnail = st.session_state.thumbnail_cache.get(thumb_key)

        if thumbnail:
            st.image(thumbnail, use_container_width=True)
            st.markdown(f"**{title['title']}**")
            st.caption(f"{title['genres']} · Rated {title['maturity_rating']}")
            if tagline:
                st.caption(f'"{tagline}"')
        else:
            tagline_html = f'<div style="font-size:0.8rem; margin-top:8px; font-style:italic;">"{tagline}"</div>' if tagline else ""
            st.markdown(
                f"""
                <div style="background-color:{title['color']}; border-radius:8px;
                            padding:16px 10px; min-height:150px; color:white;">
                    <div style="font-weight:600; font-size:0.95rem;">{title['title']}</div>
                    <div style="font-size:0.75rem; opacity:0.85; margin-top:6px;">{title['genres']}</div>
                    <div style="font-size:0.75rem; opacity:0.85;">Rated {title['maturity_rating']}</div>
                    {tagline_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.caption(f"score {title['score']} · genre {title['genre_match']} · segment {title['segment_affinity']} · pop {title['popularity']} · feedback +{title['feedback_nudge']}")
        if status == "cleared":
            st.success("✅ Cleared — available, rated within ceiling, policy OK")
            if not thumbnail:
                if st.button("🎨 Generate art", key=f"art_{title['id']}"):
                    with st.spinner("Generating stylized art..."):
                        image_bytes = ai.generate_thumbnail(title, selected_member)
                    if image_bytes:
                        st.session_state.thumbnail_cache[thumb_key] = image_bytes
                        st.rerun()
                    else:
                        st.warning("Couldn't generate art (no API key, or the call failed) — showing the style card instead.")
            if st.button("▶ Play", key=f"play_{title['id']}"):
                log_play(selected_member, title)
                st.rerun()
        else:
            st.error("🚫 Flagged — " + "; ".join(reasons))


st.subheader(f"Top picks for {selected_member['name']}")
cards = st.columns(TOP_N)
for col, (title, reasons) in zip(cards, cleared):
    render_card(col, title, "cleared", reasons)

if flagged:
    st.subheader("🔎 Needs review")
    st.caption("Flagged before display — not shown to the member, kept here for an editorial reviewer.")
    review_cols = st.columns(len(flagged))
    for col, (title, reasons) in zip(review_cols, flagged):
        render_card(col, title, "flagged", reasons)

st.divider()
st.subheader("🔁 Feedback loop")
if feedback_bonus:
    st.caption(f"Clicks so far for {selected_member['name']} are nudging these genres up in the ranking:")
    st.write(" · ".join(f"**{genre}** +{count}" for genre, count in feedback_bonus.items()))
else:
    st.caption("No plays logged yet for this member — click ▶ Play on a title above and watch the row reorder.")

member_log = [entry for entry in st.session_state.play_log if entry["member"] == selected_member["name"]]
if member_log:
    st.caption("Recent plays: " + ", ".join(entry["title"] for entry in member_log[:5]))
