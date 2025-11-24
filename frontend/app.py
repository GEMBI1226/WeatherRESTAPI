import os
import requests
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

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

# ===== MODERN CLEAN DESIGN =====
st.set_page_config(page_title="Időjárás Dashboard", layout="wide", initial_sidebar_state="expanded")

# ===== THEME CONFIGURATION =====
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# Define colors for themes
THEMES = {
    "light": {
        "bg_color": "#f5f7fa",
        "sidebar_bg": "#ffffff",
        "text_color": "#1a202c",
        "subtext_color": "#4a5568",
        "card_bg": "#ffffff",
        "border_color": "#e2e8f0",
        "primary_color": "#3182ce",
        "secondary_text": "#718096",
        "shadow": "rgba(0,0,0,0.1)",
        "chart_bg": "white",
        "chart_text": "#2d3748"
    },
    "dark": {
        "bg_color": "#1a202c",
        "sidebar_bg": "#2d3748",
        "text_color": "#ffffff",
        "subtext_color": "#e2e8f0",
        "card_bg": "#2d3748",
        "border_color": "#4a5568",
        "primary_color": "#63b3ed",
        "secondary_text": "#cbd5e0",
        "shadow": "rgba(0,0,0,0.3)",
        "chart_bg": "#2d3748",
        "chart_text": "#ffffff"
    }
}

current_theme = THEMES[st.session_state.theme]

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    /* Clean background */
    .stApp {{
        background: {current_theme['bg_color']};
    }}
    
    /* Hide default elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Title */
    h1 {{
        color: {current_theme['text_color']};
        font-weight: 700;
        padding: 1rem 0;
    }}
    
    h2, h3 {{
        color: {current_theme['text_color']};
        font-weight: 600;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {current_theme['sidebar_bg']};
        border-right: 1px solid {current_theme['border_color']};
    }}

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        color: {current_theme['text_color']};
    }}
    
    [data-testid="stSidebar"] label {{
        color: {current_theme['text_color']};
    }}
    
    /* Weather cards */
    .weather-card {{
        background: {current_theme['card_bg']};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid {current_theme['border_color']};
        box-shadow: 0 1px 3px {current_theme['shadow']};
        transition: box-shadow 0.2s ease;
    }}
    
    .weather-card:hover {{
        box-shadow: 0 4px 6px {current_theme['shadow']};
    }}
    
    .city-name {{
        font-size: 1.25rem;
        font-weight: 600;
        color: {current_theme['text_color']};
        margin-bottom: 0.5rem;
    }}
    
    .temperature {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {current_theme['primary_color']};
    }}
    
    .weather-detail {{
        color: {current_theme['subtext_color']};
        font-size: 0.95rem;
        margin: 0.3rem 0;
    }}
    
    /* Stats cards */
    .stat-card {{
        background: {current_theme['card_bg']};
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid {current_theme['border_color']};
        box-shadow: 0 1px 3px {current_theme['shadow']};
    }}
    
    .stat-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {current_theme['primary_color']};
    }}
    
    .stat-label {{
        color: {current_theme['secondary_text']};
        font-size: 0.875rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }}
    
    /* Buttons */
    .stButton > button {{
        background: {current_theme['primary_color']};
        color: {current_theme['card_bg'] if st.session_state.theme == 'dark' else 'white'};
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: background 0.2s ease;
    }}
    
    .stButton > button:hover {{
        opacity: 0.9;
    }}
    
    /* Chart container */
    .chart-container {{
        background: {current_theme['card_bg']};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid {current_theme['border_color']};
        box-shadow: 0 1px 3px {current_theme['shadow']};
    }}
    
    /* Info box in sidebar */
    .info-box {{
        color: {current_theme['subtext_color']};
        margin: 1rem 0;
        padding: 1rem;
        background: {current_theme['bg_color']};
        border-radius: 8px;
        border: 1px solid {current_theme['border_color']};
    }}
    .info-box strong {{
        color: {current_theme['text_color']};
    }}
</style>
""", unsafe_allow_html=True)

st.title("🌤️ Időjárás Dashboard")

# ===== SIDEBAR =====
with st.sidebar:
    st.header("⚙️ Beállítások")
    
    # Dark mode toggle
    st.toggle("🌙 Sötét mód", value=(st.session_state.theme == "dark"), on_change=toggle_theme)
    
    city_names = [c[0] for c in CITIES]
    selected_city = st.selectbox("🏙️ Város", city_names, index=1)
    sel_lat, sel_lon = CITY_NAME_TO_COORDS[selected_city]
    
    st.markdown(f"""
    <div class='info-box'>
        <strong>📍 Koordináták:</strong><br/>
        Szélesség: {sel_lat}<br/>
        Hosszúság: {sel_lon}
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("💾 Mentés", use_container_width=True):
        try:
            r = requests.post(
                f"{BACKEND}/weather/fetch",
                params={"lat": sel_lat, "lon": sel_lon},
                timeout=15,
            )
            if r.ok:
                st.success(f"✅ {selected_city}")
                st.rerun()
            else:
                st.error(f"❌ {r.status_code}")
        except Exception as e:
            st.error(f"🔌 Hiba: {e}")
    
    st.markdown("---")
    
    if st.button("🗑️ Adatbázis törlése", use_container_width=True, type="secondary"):
        try:
            r = requests.delete(f"{BACKEND}/weather/reset", timeout=15)
            if r.ok:
                st.success("✅ Adatbázis törölve!")
                st.rerun()
            else:
                st.error(f"❌ Hiba: {r.status_code}")
        except Exception as e:
            st.error(f"🔌 Hiba: {e}")

# ===== STATISZTIKÁK =====
try:
    stats_response = requests.get(f"{BACKEND}/weather/stats", timeout=15)
    stats = stats_response.json() if stats_response.ok else None
except Exception:
    stats = None

if stats and stats.get("count", 0) > 0:
    st.markdown("### 📊 Statisztikák")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-value'>{stats['count']}</div>
            <div class='stat-label'>📝 Összes mérés</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-value'>{stats['avg_temp']}°C</div>
            <div class='stat-label'>🌡️ Átlag hőmérséklet</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-value'>{stats['min_temp']}°C / {stats['max_temp']}°C</div>
            <div class='stat-label'>❄️ Min / 🔥 Max</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-value'>{stats['avg_wind']} km/h</div>
            <div class='stat-label'>💨 Átlag szél</div>
        </div>
        """, unsafe_allow_html=True)

# ===== ADATOK LEKÉRÉSE =====
st.markdown("### 🏙️ Aktuális időjárás városonként")

try:
    r = requests.get(f"{BACKEND}/weather", timeout=15)
    data = r.json() if r.ok else []
except Exception:
    data = []

if not data:
    st.info("📭 Még nincsenek adatok. Kattints a bal oldalon a mentésre!")
else:
    df = pd.DataFrame(data)
    df["fetched_at"] = pd.to_datetime(df["fetched_at"])
    df = df.sort_values("fetched_at")
    
    def city_name_from_coords(row):
        for name, lat, lon in CITIES:
            if abs(row["latitude"] - lat) < 1e-4 and abs(row["longitude"] - lon) < 1e-4:
                return name
        return "Ismeretlen"
    
    df["city"] = df.apply(city_name_from_coords, axis=1)
    df = df[df["city"] != "Ismeretlen"]
    
    if df.empty:
        st.warning("⚠️ Még nincs mentés az előre beállított városokra.")
    else:
        # ===== WEATHER CARDS =====
        latest_data = df.sort_values("fetched_at").groupby("city").last().reset_index()
        
        def get_weather_emoji(temp):
            if temp < 0:
                return "❄️"
            elif temp < 10:
                return "🌤️"
            elif temp < 20:
                return "⛅"
            elif temp < 30:
                return "☀️"
            else:
                return "🔥"
        
        cols = st.columns(3)
        for idx, row in latest_data.iterrows():
            with cols[idx % 3]:
                emoji = get_weather_emoji(row["temperature_c"])
                last_update = row["fetched_at"].strftime("%Y-%m-%d %H:%M")
                
                st.markdown(f"""
                <div class='weather-card'>
                    <div class='city-name'>{emoji} {row['city']}</div>
                    <div class='temperature'>{row['temperature_c']:.1f}°C</div>
                    <div class='weather-detail'>💨 Szél: {row['windspeed_kmh']:.1f} km/h</div>
                    <div class='weather-detail' style='font-size: 0.85rem; color: {current_theme['secondary_text']};'>
                        🕐 {last_update}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # ===== TEMPERATURE CHART =====
        st.markdown("### 📈 Hőmérséklet alakulása")
        
        temp_chart = (
            alt.Chart(df)
            .mark_line(point=True, strokeWidth=2.5)
            .encode(
                x=alt.X("fetched_at:T", title="Időpont", axis=alt.Axis(labelColor=current_theme['chart_text'], titleColor=current_theme['chart_text'])),
                y=alt.Y("temperature_c:Q", title="Hőmérséklet (°C)", axis=alt.Axis(labelColor=current_theme['chart_text'], titleColor=current_theme['chart_text'])),
                color=alt.Color("city:N", title="Város", scale=alt.Scale(scheme="category10"), legend=alt.Legend(labelColor=current_theme['chart_text'], titleColor=current_theme['chart_text'])),
                tooltip=[
                    alt.Tooltip("city:N", title="Város"),
                    alt.Tooltip("fetched_at:T", title="Időpont", format="%Y-%m-%d %H:%M"),
                    alt.Tooltip("temperature_c:Q", title="Hőmérséklet (°C)", format=".1f"),
                    alt.Tooltip("windspeed_kmh:Q", title="Szélsebesség (km/h)", format=".1f"),
                ],
            )
            .properties(height=400, background=current_theme['chart_bg'])
            .configure_axis(
                gridColor=current_theme['border_color']
            )
            .configure_view(
                strokeWidth=0
            )
        )
        
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.altair_chart(temp_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # ===== WIND CHART =====
        st.markdown("### 💨 Szélsebesség alakulása")
        
        wind_chart = (
            alt.Chart(df)
            .mark_line(point=True, strokeWidth=2.5)
            .encode(
                x=alt.X("fetched_at:T", title="Időpont", axis=alt.Axis(labelColor=current_theme['chart_text'], titleColor=current_theme['chart_text'])),
                y=alt.Y("windspeed_kmh:Q", title="Szélsebesség (km/h)", axis=alt.Axis(labelColor=current_theme['chart_text'], titleColor=current_theme['chart_text'])),
                color=alt.Color("city:N", title="Város", scale=alt.Scale(scheme="category10"), legend=alt.Legend(labelColor=current_theme['chart_text'], titleColor=current_theme['chart_text'])),
                tooltip=[
                    alt.Tooltip("city:N", title="Város"),
                    alt.Tooltip("fetched_at:T", title="Időpont", format="%Y-%m-%d %H:%M"),
                    alt.Tooltip("temperature_c:Q", title="Hőmérséklet (°C)", format=".1f"),
                    alt.Tooltip("windspeed_kmh:Q", title="Szélsebesség (km/h)", format=".1f"),
                ],
            )
            .properties(height=400, background=current_theme['chart_bg'])
            .configure_axis(
                gridColor=current_theme['border_color']
            )
            .configure_view(
                strokeWidth=0
            )
        )
        
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.altair_chart(wind_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
