import os
import requests
import streamlit as st
import pandas as pd
import altair as alt

BACKEND = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Beadandó – Időjárás", layout="wide")
st.title("Időjárás – Streamlit frontend (FastAPI backend)")

with st.sidebar:
    st.header("Beállítások")
    lat = st.number_input("Szélesség (lat)", value=47.4979)
    lon = st.number_input("Hosszúság (lon)", value=19.0402)
    if st.button("Friss mérés mentése"):
        r = requests.post(
            f"{BACKEND}/weather/fetch", 
            params={"lat": lat, "lon": lon}, 
            timeout=15
        )
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
    # --- DataFrame előkészítés ---
    df = pd.DataFrame(data)
    df["fetched_at"] = pd.to_datetime(df["fetched_at"])
    df = df.sort_values("fetched_at")  # időrendbe tesszük

    # ---- HŐMÉRSÉKLET GRAFIKON ----
    temp_chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("fetched_at:T", title="Időpont"),
            y=alt.Y("temperature_c:Q", title="Hőmérséklet (°C)"),
            tooltip=[
                alt.Tooltip("fetched_at:T", title="Időpont"),
                alt.Tooltip("temperature_c:Q", title="Hőmérséklet (°C)"),
                alt.Tooltip("windspeed_kmh:Q", title="Szélsebesség (km/h)"),
                alt.Tooltip("latitude:Q", title="Szélesség"),
                alt.Tooltip("longitude:Q", title="Hosszúság"),
            ],
        )
        .properties(title="Hőmérséklet alakulása időben")
    )

    st.altair_chart(temp_chart, use_container_width=True)

    # ---- SZÉLSEBESSÉG GRAFIKON ----
    wind_chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("fetched_at:T", title="Időpont"),
            y=alt.Y("windspeed_kmh:Q", title="Szélsebesség (km/h)"),
            tooltip=[
                alt.Tooltip("fetched_at:T", title="Időpont"),
                alt.Tooltip("temperature_c:Q", title="Hőmérséklet (°C)"),
                alt.Tooltip("windspeed_kmh:Q", title="Szélsebesség (km/h)"),
                alt.Tooltip("latitude:Q", title="Szélesség"),
                alt.Tooltip("longitude:Q", title="Hosszúság"),
            ],
        )
        .properties(title="Szélsebesség alakulása időben")
    )

    st.altair_chart(wind_chart, use_container_width=True)
