import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from analyse import plot_laufdaten

DB_PATH = "laufdaten.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS laufdaten (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                distanz_km REAL,
                pace REAL,
                avg_hf REAL,
                max_hf REAL,
                hm REAL,
                benutzer_id TEXT
            )
        """)
        conn.commit()

def daten_speichern(datum, distanz, pace, avg_hf, max_hf, hm, benutzer_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO laufdaten (date, distanz_km, pace, avg_hf, max_hf, hm, benutzer_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (datum, distanz, pace, avg_hf, max_hf, hm, benutzer_id)
        )
        conn.commit()

def lade_daten(benutzer_id):
    with sqlite3.connect(DB_PATH) as conn:
        # Params als Tuple (benutzer_id,) wichtig!
        df = pd.read_sql_query(
            "SELECT * FROM laufdaten WHERE benutzer_id = ?", 
            conn, 
            params=(benutzer_id,)
        )
    return df

# -------------------- Haupt-App --------------------

st.title("🏃 Laufanalyse")
init_db()

if "benutzername" not in st.session_state:
    st.session_state.benutzername = ""

if st.session_state.benutzername == "":
    # Login-Seite
    st.sidebar.title("Benutzer Login")
    eingabe_name = st.sidebar.text_input("Benutzername eingeben")

    if st.sidebar.button("Login"):
        if eingabe_name.strip() == "":
            st.sidebar.warning("Bitte gib einen Benutzernamen ein.")
        else:
            st.session_state.benutzername = eingabe_name.strip()
            st.experimental_rerun()

else:
    # Hauptseite
    st.sidebar.write(f"👤 Angemeldet als: **{st.session_state.benutzername}**")
    if st.sidebar.button("Logout"):
        st.session_state.benutzername = ""
        st.experimental_rerun()

    with st.form("Laufdaten Formular"):
        datum = st.text_input("Datum (DD-MM-YYYY)")
        distanz = st.number_input("Distanz (km)", step=0.1)
        pace = st.number_input("Pace (min/km)", step=0.1)
        avg_hf = st.number_input("Durchschnittliche HF", step=1)
        max_hf = st.number_input("Maximale HF", step=1)
        hm = st.number_input("Höhenmeter", step=1)
        submitted = st.form_submit_button("💾 Speichern")

        if submitted:
            try:
                datetime.strptime(datum, "%d-%m-%Y")
                daten_speichern(datum, distanz, pace, avg_hf, max_hf, hm, st.session_state.benutzername)
                st.success("✅ Laufdaten gespeichert!")
            except Exception as e:
                st.error(f"❌ Fehler beim Speichern: {e}")

    df = lade_daten(st.session_state.benutzername)

    if not df.empty:
        st.subheader("📋 Gespeicherte Läufe")
        st.dataframe(df.sort_values(by="date", ascending=False))
        st.divider()
        plot_laufdaten(df)
    else:
        st.info("Noch keine Laufdaten vorhanden.")
