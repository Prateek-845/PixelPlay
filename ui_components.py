import streamlit as st
from collections import Counter
import logic  

def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #E0E0E0; }
        .stApp { background-color: #050505; }
        .block-container { padding-top: 2rem; padding-bottom: 5rem; }
        h1, h2, h3 { font-weight: 700; color: #FFFFFF; }
        .main-header { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; text-align: center; margin-top: 2rem; }
        .sub-header { font-size: 1rem; color: #888888; font-weight: 400; text-align: center; margin-bottom: 3rem; }
        div[data-testid="stButton"] button { background-color: #1DB954; color: #000000; border: none; font-weight: 600; padding: 0.5rem 1rem; border-radius: 4px; transition: all 0.2s; }
        div[data-testid="stButton"] button:hover { background-color: #1ed760; transform: translateY(-1px); }
        div[data-testid="stVerticalBlockBorderWrapper"] > div { background-color: #121212; border: 1px solid #222; border-radius: 8px; padding: 16px; }
        .tag-container { display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; }
        .pro-tag { background-color: #1A1A1A; border: 1px solid #333; color: #AAA; padding: 4px 12px; border-radius: 100px; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; }
        .pro-tag.accent { border-color: #1DB954; color: #1DB954; background-color: rgba(29, 185, 84, 0.1); }
        hr { border-color: #222; margin: 3rem 0; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def render_login_header():
    st.markdown('<div class="main-header">PixelPlay</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Professional Audio Intelligence</div>', unsafe_allow_html=True)

def display_vibe_summary(df_results):
    if len(df_results) == 0: return
    genres = df_results['genre'].fillna('Unknown').tolist()
    most_common_genre = Counter(genres).most_common(1)[0][0] if genres else "Various"
    avg_energy = df_results['energy'].mean()
    avg_valence = df_results['valence'].mean()
    energy_tag = "High Energy" if avg_energy > 0.6 else "Low Energy"
    mood_tag = "Positive" if avg_valence > 0.6 else ("Melancholic" if avg_valence < 0.4 else "Neutral")
    
    st.markdown(f"""
    <div class="tag-container">
        <div class="pro-tag accent">{most_common_genre}</div>
        <div class="pro-tag">{mood_tag}</div>
        <div class="pro-tag">{energy_tag}</div>
    </div>
    """, unsafe_allow_html=True)

def render_song_card(row, score, df_full, embeddings_full):
    song_data = logic.fetch_song_details_fast(row)
    
    with st.container(border=True):
        col_art, col_details, col_viz, col_actions = st.columns([2, 4, 2.5, 2])
        
        with col_art:
            st.image(song_data['image'], use_container_width=True)
        with col_details:
            st.markdown(f"<div style='font-weight:600; font-size:1.1rem; margin-bottom:4px;'>{row['name']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:#888; font-size:0.9rem; margin-bottom:8px;'>{row['artist']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:#555; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;'>{row['genre']} • {int(row['year'])}</div>", unsafe_allow_html=True)
            if song_data['audio']:
                st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
                st.audio(song_data['audio'], format="audio/m4a", start_time=0)
        with col_viz:
            st.plotly_chart(logic.create_radar_chart(row), use_container_width=True, config={'displayModeBar': False}, key=f"radar_{row.name}")
        with col_actions:
            st.markdown(f"<div style='font-size:1.5rem; font-weight:700; color:#1DB954; text-align:right;'>{int(score*100)}%</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:0.7rem; color:#444; text-align:right; margin-bottom:12px; letter-spacing:0.05em;'>MATCH</div>", unsafe_allow_html=True)
            spotify_url = f"https://open.spotify.com/track/{row['id']}"
            st.markdown(f"<div style='text-align:right; margin-bottom:12px;'><a href='{spotify_url}' target='_blank' style='color:#E0E0E0; text-decoration:none; font-size:0.8rem; border-bottom:1px dotted #555;'>Spotify ↗</a></div>", unsafe_allow_html=True)
            
            if st.button("Find Similar", key=f"btn_{row.name}"):
                global_idx = df_full.index.get_loc(row.name) if isinstance(row.name, int) else df_full[df_full['id'] == row['id']].index[0]
                st.session_state.search_vector = embeddings_full[global_idx].reshape(1, -1) 
                st.session_state.search_source = "song"
                st.session_state.search_offset = 0
                st.rerun()