import os
import requests
import streamlit as st
import pandas as pd
import altair as alt

BACKEND = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# ===== VÁROSOK LISTÁJA =====
CITIES = [
    ("Budapest", 47.4979, 19.0402),
    ("Eger", 47.902534, 20.377228),
    ("Debrecen", 47.531605, 21.627312),
    ("Szeged", 46.253, 20.141),
    ("Pécs", 46.0727, 18.2323),
]

CITY_NAME_TO_COORDS = {name: (lat, lon) for name, lat, lon in CITIES}

st.set_page_config(page_title="Beadandó – Időjárás", layout="wide")
st.title("Időjárás – Streamlit frontend (FastAPI backend)")


# ===== SIDEBAR – VÁROS VÁLASZTÁS + MENTÉS =====
with st.sidebar:
    st.header("Beállítások")

    city_names = [c[0] for c in CITIES]
    selected_city = st.selectbox("Város", city_names, index=1)  # pl. Eger default
    sel_lat, sel_lon = CITY_NAME_TO_COORDS[selected_city]

    st.write(f"**Szélesség (lat):** {sel_lat}")
    st.write(f"**Hosszúság (lon):** {sel_lon}")

    if st.button("Friss mérés mentése a kiválasztott városhoz"):
        try:
            r = requests.post(
                f"{BACKEND}/weather/fetch",
                params={"lat": sel_lat, "lon": sel_lon},
                timeout=15,
            )
            if r.ok:
                st.success(f"Mentve: {selected_city}")
            else:
                st.error(f"Hiba: {r.status_code} – {r.text}")
        except Exception as e:
            st.error(f"Hálózati hiba: {e}")


# ===== ADATOK LEKÉRÉSE A BACKENDTŐL =====
st.subheader("Mérések (összes város)")

try:
    r = requests.get(f"{BACKEND}/weather", timeout=15)
    data = r.json() if r.ok else []
except Exception:
    data = []

if not data:
    st.info("Még nincsenek adatok. Kattints a bal oldalon a frissítésre!")
else:
    # ---- DataFrame készítés ----
    df = pd.DataFrame(data)

    # időbélyeg konvertálás + sorrend
    df["fetched_at"] = pd.to_datetime(df["fetched_at"])
    df = df.sort_values("fetched_at")

    # városnév hozzárendelése a koordinátákból
    def city_name_from_coords(row):
        for name, lat, lon in CITIES:
            if abs(row["latitude"] - lat) < 1e-4 and abs(row["longitude"] - lon) < 1e-4:
                return name
        return "Ismeretlen"

    df["city"] = df.apply(city_name_from_coords, axis=1)

    # kis szűrő: csak az általad definiált 5 város
    df = df[df["city"] != "Ismeretlen"]

    if df.empty:
        st.warning("Még nincs mentés az előre beállított városokra.")
    else:
        # ===== HŐMÉRSÉKLET GRAFIKON – X: IDŐ, Y: HŐ, SZÍN: VÁROS =====
        temp_chart = (
            alt.Chart(df)
            .mark_line(point=True)
            .encode(
                x=alt.X("fetched_at:T", title="Mentés időpontja"),
                y=alt.Y("temperature_c:Q", title="Hőmérséklet (°C)"),
                color=alt.Color("city:N", title="Város"),
                tooltip=[
                    alt.Tooltip("city:N", title="Város"),
                    alt.Tooltip("fetched_at:T", title="Időpont"),
                    alt.Tooltip("temperature_c:Q", title="Hőmérséklet (°C)"),
                    alt.Tooltip("windspeed_kmh:Q", title="Szélsebesség (km/h)"),
                    alt.Tooltip("latitude:Q", title="Szélesség"),
                    alt.Tooltip("longitude:Q", title="Hosszúság"),
                ],
            )
            .properties(title="Hőmérséklet alakulása 5 városban")
        )

        st.altair_chart(temp_chart, use_container_width=True)

        # ===== SZÉLSEBESSÉG GRAFIKON – X: IDŐ, Y: SZÉL, SZÍN: VÁROS =====
        wind_chart = (
            alt.Chart(df)
            .mark_line(point=True)
            .encode(
                x=alt.X("fetched_at:T", title="Mentés időpontja"),
                y=alt.Y("windspeed_kmh:Q", title="Szélsebesség (km/h)"),
                color=alt.Color("city:N", title="Város"),
                tooltip=[
                    alt.Tooltip("city:N", title="Város"),
                    alt.Tooltip("fetched_at:T", title="Időpont"),
                    alt.Tooltip("temperature_c:Q", title="Hőmérséklet (°C)"),
                    alt.Tooltip("windspeed_kmh:Q", title="Szélsebesség (km/h)"),
                    alt.Tooltip("latitude:Q", title="Szélesség"),
                    alt.Tooltip("longitude:Q", title="Hosszúság"),
                ],
            )
            .properties(title="Szélsebesség alakulása 5 városban")
        )

        st.altair_chart(wind_chart, use_container_width=True)
