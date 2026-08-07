import streamlit as st

st.set_page_config(
    page_title="CareerOS AI",
    page_icon="💼",
    layout="wide"
)

st.title("💼 CareerOS AI")
st.subheader("AI-Powered Job Search & Application Assistant")

st.write(
    "Smart job search, matching and application assistance "
    "for the Romanian and European job market."
)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Jobs Found", "0")

with col2:
    st.metric("Best Match", "0%")

with col3:
    st.metric("Applications", "0")

st.divider()

st.header("🎯 Job Search Profile")

st.write("Candidate: Ahmed")

st.write("📍 Location: Timișoara, Romania")
st.write("🗣️ Languages: Arabic / English / Romanian (beginner)")
st.write("🎓 Education: Master's Degree in Law")
st.write("💼 Experience: 10+ years")
st.write("🎯 Target Salary: 3,000–7,000 RON")

st.info(
    "The AI job agent will search, analyze and rank suitable jobs "
    "based on the candidate profile."
)
