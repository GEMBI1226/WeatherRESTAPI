
# README

## Weather REST API -- Python beadandó

Ez a projekt egy egyszerű, mikroszerviz-szerű Python alkalmazás, amely
egy FastAPI alapú backendből és egy Streamlit frontendből áll.
A rendszer külső API-ból időjárásadatokat kér le, eltárolja az
adatbázisban, és megjeleníti egy webes felületen.

------------------------------------------------------------------------

## Telepítés

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

------------------------------------------------------------------------

## Főbb komponensek

### Backend (FastAPI)

- REST API végpontok
- Külső API hívás (Open-Meteo)
- SQLAlchemy ORM
- Pydantic sémák
- SQLite adatbázis
- Időzített automatikus adatmentés
- Időzített automatikus e-mail küldés

Indítás:

    uvicorn backend.app:app --reload

### Frontend (Streamlit)

A Streamlit alkalmazás meghívja a FastAPI végpontjait és megjeleníti az adatokat.

Indítás:

    streamlit run frontend/app.py

------------------------------------------------------------------------

## Mappa struktúra

    app/
      api/
      core/
      crud/
      database/
      models/
      schemas/
      services/
      main.py
    frontend/
      app.py
    tests/

------------------------------------------------------------------------

## Automatizálás

- időzített adatmentés
- időzített e-mail küldés

------------------------------------------------------------------------

## Tesztelés

A projekt összesen **23 sikeres pytest tesztet** tartalmaz, amelyek lefedik a teljes szolgáltatáslogikát, hibakezelést és az integrációs folyamatokat.

    pytest
