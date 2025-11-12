#!/usr/bin/env bash
set -e
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi
(uvicorn backend.app:app --reload &)
streamlit run frontend/app.py
