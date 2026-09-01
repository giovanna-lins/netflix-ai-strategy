import streamlit as st

import logic

st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")

st.title("🎬 CineMatch")
st.caption("Grounded personalized discovery — classroom MVP")

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
ranked = logic.rank_titles(selected_member, catalog, weights)

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
        st.markdown(
            f"""
            <div style="background-color:{title['color']}; border-radius:8px;
                        padding:16px 10px; min-height:150px; color:white;">
                <div style="font-weight:600; font-size:0.95rem;">{title['title']}</div>
                <div style="font-size:0.75rem; opacity:0.85; margin-top:6px;">{title['genres']}</div>
                <div style="font-size:0.75rem; opacity:0.85;">Rated {title['maturity_rating']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(f"score {title['score']} · genre {title['genre_match']} · segment {title['segment_affinity']} · pop {title['popularity']}")
        if status == "cleared":
            st.success("✅ Cleared — available, rated within ceiling, policy OK")
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
