# laufanalyse_app.py

import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from analyse import plot_laufdaten


DB_PATH = "laufdaten.db"

# --------------------------
# Benutzer-Login
# --------------------------
st.sidebar.title("Benutzer Login")
benutzername = st.sidebar.text_input("Benutzername", value="gast")

if not benutzername:
    st.warning("Bitte gib einen Benutzernamen ein.")
    st.stop()

# --------------------------
# DB initialisieren
# --------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()

# --------------------------
# Daten speichern
# --------------------------
def daten_speichern(datum, distanz, pace, avg_hf, max_hf, hm, benutzer_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO laufdaten (date, distanz_km, pace, avg_hf, max_hf, hm, benutzer_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (datum, distanz, pace, avg_hf, max_hf, hm, benutzer_id)
    )
    conn.commit()
    conn.close()

# --------------------------
# Daten laden
# --------------------------
def lade_daten(benutzer_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM laufdaten WHERE benutzer_id = ?", conn, params=(benutzer_id,))
    conn.close()
    return df

# --------------------------
# Analysefunktion
# --------------------------
def z_score(arr):
    return (arr - np.mean(arr)) / np.std(arr)

def einfache_analyse(df):
    st.subheader("📈 Z-Score Trends")

    datums = pd.to_datetime(df['date'], format="%d-%m-%Y")
    df = df.assign(datums=datums)

    df = df.sort_values(by="datums")

    for col in ['distanz_km', 'pace', 'avg_hf']:
        df[f"{col}_z"] = z_score(df[col])

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['datums'], df['distanz_km_z'], label='Distanz (Z)')
    ax.plot(df['datums'], df['pace_z'], label='Pace (Z)')
    ax.plot(df['datums'], df['avg_hf_z'], label='Avg HF (Z)')
    ax.axhline(0, color='gray', linestyle='--')
    ax.set_title("Z-Scores über Zeit")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # Textliche Analyse
    trend = df['pace'].rolling(3).mean().diff().mean()
    if trend < -0.05:
        st.success("🏃 Deine Pace verbessert sich!")
    elif trend > 0.05:
        st.warning("⚠️ Deine Pace wird langsamer.")
    else:
        st.info("🔄 Deine Pace bleibt stabil.")

# --------------------------
# Streamlit App Start
# --------------------------
st.title("🏃 Laufanalyse")
init_db()

# Eingabeformular
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
            daten_speichern(datum, distanz, pace, avg_hf, max_hf, hm, benutzername)
            st.success("✅ Laufdaten gespeichert!")
        except Exception as e:
            st.error(f"❌ Fehler beim Speichern: {e}")

# Daten laden & analysieren
df = lade_daten(benutzername)

if not df.empty:
    st.subheader("📋 Gespeicherte Läufe")
    st.dataframe(df.sort_values(by="date", ascending=False))

    st.divider()

    plot_laufdaten(df)  # Hier wird jetzt im Streamlit das Plot angezeigt
else:
    st.info("Noch keine Laufdaten vorhanden.")




