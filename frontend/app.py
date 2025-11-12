import os
import requests
import streamlit as st

BACKEND = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Beadandó – Időjárás", layout="wide")
st.title("Időjárás – Streamlit frontend (FastAPI backend)")

with st.sidebar:
    st.header("Beállítások")
    lat = st.number_input("Szélesség (lat)", value=47.4979)
    lon = st.number_input("Hosszúság (lon)", value=19.0402)
    if st.button("Friss mérés mentése"):
        r = requests.post(f"{BACKEND}/weather/fetch", params={"lat": lat, "lon": lon}, timeout=15)
        if r.ok:
            st.success("Mentve!")
        else:
            st.error(f"Hiba: {r.text}")

st.subheader("Mérések")
try:
    r = requests.get(f"{BACKEND}/weather", timeout=15)
    data = r.json() if r.ok else []
except Exception:
    data = []

if not data:
    st.info("Még nincsenek adatok. Kattints a bal oldalon a frissítésre!")
else:
    temps = [row["temperature_c"] for row in data]
    winds = [row["windspeed_kmh"] for row in data]
    st.line_chart(temps)
    st.line_chart(winds)