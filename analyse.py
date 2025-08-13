import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st  # unbedingt importieren

def z_score(arr):
    return (arr - np.mean(arr)) / np.std(arr)

def plot_laufdaten(df):
    df['datums'] = pd.to_datetime(df['date'], format="%d-%m-%Y")
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
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)  # statt plt.show()
