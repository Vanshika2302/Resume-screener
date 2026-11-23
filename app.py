"""Streamlit UI. Run: streamlit run app.py (backend must be running)"""
import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/screen"

st.set_page_config(page_title="Resume Screener", page_icon="📄")
st.title("📄 Resume Screener")

files = st.file_uploader("Upload resumes (PDF)", type="pdf", accept_multiple_files=True)
jd = st.text_area("Paste job description", height=200)

if st.button("Screen", type="primary"):
    if not files or not jd.strip():
        st.warning("Upload at least one resume and paste a job description.")
    else:
        with st.spinner("Analyzing..."):
            try:
                resp = requests.post(
                    API_URL,
                    files=[("resumes", (f.name, f.getvalue(), "application/pdf")) for f in files],
                    data={"jd": jd},
                    timeout=300,
                )
                resp.raise_for_status()
                results = resp.json()["results"]
            except Exception as e:
                st.error(f"Request failed: {e}")
                st.stop()

        ok = [r for r in results if "error" not in r]
        bad = [r for r in results if "error" in r]

        if ok:
            st.subheader("Ranking")
            st.dataframe(
                pd.DataFrame(
                    [{"File": r["filename"], "Name": r["candidate"]["name"],
                      "Match %": r["match_score"],
                      "Experience (yrs)": r["candidate"]["years_experience"]} for r in ok]
                ),
                hide_index=True,
            )
            for r in ok:
                with st.expander(f"{r['candidate']['name']} - {r['match_score']}%"):
                    st.write("**Skills:**", ", ".join(r["candidate"]["skills"]))
                    st.write("**Education:**", r["candidate"]["education"])
                    st.markdown(r["analysis"])
        for r in bad:
            st.error(f"{r['filename']}: {r['error']}")
