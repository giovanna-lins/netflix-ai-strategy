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
