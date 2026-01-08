import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objects as go
from sentence_transformers import SentenceTransformer
import requests

@st.cache_data
def load_data():
    try:
        with open('songs_enriched.pkl', 'rb') as f:
            data = pickle.load(f)
        return data['df'], data['embeddings']
    except FileNotFoundError:
        st.error("error: 'songs_enriched.pkl' not found")
        st.stop()

@st.cache_resource
def load_model():
    return SentenceTransformer('clip-ViT-B-32')

def fetch_song_details_fast(row):
    return {
        'image': row.get('album_art') if row.get('album_art') else "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/12in-Vinyl-LP-Record-Angle.jpg/640px-12in-Vinyl-LP-Record-Angle.jpg",
        'audio': row.get('preview_url')
    }

def create_radar_chart(row):
    categories = ['Energy', 'Valence', 'Dance', 'Acoustic']
    values = [row['energy'], row['valence'], row['danceability'], row['acousticness']]
    values += values[:1]
    categories += categories[:1]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values, theta=categories, fill='toself', 
        line_color='#1DB954', fillcolor='rgba(29, 185, 84, 0.1)', 
        marker=dict(size=0)
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1]), 
            bgcolor='rgba(0,0,0,0)', 
            gridshape='linear',
            angularaxis=dict(tickfont=dict(size=8, color="#666"))
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=15, b=15),
        height=140,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig