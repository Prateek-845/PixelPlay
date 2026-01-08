import streamlit as st
import numpy as np
from sentence_transformers import util
from PIL import Image
import auth_manager
import logic
import ui_components

st.set_page_config(page_title="PixelPlay", layout="wide", initial_sidebar_state="expanded")

ui_components.inject_custom_css()

if 'search_offset' not in st.session_state: st.session_state.search_offset = 0
if 'last_uploaded_file' not in st.session_state: st.session_state.last_uploaded_file = None
if 'search_vector' not in st.session_state: st.session_state.search_vector = None
if 'search_source' not in st.session_state: st.session_state.search_source = "image"

authenticator, config = auth_manager.setup_authenticator()

if st.session_state.get("authentication_status") is None or st.session_state.get("authentication_status") is False:
    ui_components.render_login_header()
    auth_manager.show_login_flow(authenticator, config)

elif st.session_state["authentication_status"]:    
    model = logic.load_model()
    df_full, song_embeddings_full = logic.load_data()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"<div style='color: #666; font-size: 0.8rem; margin-bottom: 20px;'>LOGGED IN AS <b>{st.session_state['name'].upper()}</b></div>", unsafe_allow_html=True)
        st.markdown("### DATA SOURCE")
        uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("### FILTERING")
        all_genres = sorted(df_full['genre'].astype(str).unique())
        selected_genres = st.multiselect("Genre Select", all_genres)
        min_year = int(df_full['year'].min())
        max_year = int(df_full['year'].max())
        selected_years = st.slider("Time Period", min_year, max_year, (min_year, max_year))
        
        st.markdown("---")
        st.markdown("### REFINEMENT")
        text_modifier = st.text_input("Context Hint", placeholder="e.g. 'Industrial', 'Warm'")
        alpha = st.slider("Text Weight", 0.0, 1.0, 0.3)
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        if c1.button("Reset"):
            st.session_state.search_offset = 0
            st.session_state.search_vector = None
            st.session_state.search_source = "image"
            st.rerun()
        with c2:
            authenticator.logout('Logout', 'main', key='unique_logout_btn')

    ui_components.render_login_header() 
    if uploaded_file is not None:
        if uploaded_file != st.session_state.last_uploaded_file:
            st.session_state.last_uploaded_file = uploaded_file
            st.session_state.search_offset = 0
            st.session_state.search_source = "image"
            
        image = Image.open(uploaded_file)
        
        # Filter
        filtered_df = df_full.copy()
        if selected_genres:
            filtered_df = filtered_df[filtered_df['genre'].isin(selected_genres)]
        filtered_df = filtered_df[(filtered_df['year'] >= selected_years[0]) & (filtered_df['year'] <= selected_years[1])]
        
        if len(filtered_df) == 0:
            st.error("No matches found within selected filters.")
        else:
            filtered_indices = filtered_df.index
            filtered_embeddings = song_embeddings_full[filtered_indices]

            # Display Image & Search Status
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image(image, use_container_width=True)
                with st.spinner("Processing visual features..."):
                    if st.session_state.search_source == "song" and st.session_state.search_vector is not None:
                        final_emb = st.session_state.search_vector
                        st.info("Searching based on selected audio track.")
                        if st.button("← Return to Visual Search"):
                            st.session_state.search_source = "image"
                            st.session_state.search_vector = None
                            st.session_state.search_offset = 0
                            st.rerun()
                    else:
                        img_emb = model.encode(image)
                        if text_modifier:
                            text_emb = model.encode(text_modifier)
                            final_emb = ((1 - alpha) * img_emb) + (alpha * text_emb)
                        else:
                            final_emb = img_emb

                    scores = util.cos_sim(final_emb, filtered_embeddings)[0]
                    sorted_indices = scores.argsort(descending=True)
                    
                    if st.session_state.search_source == "song":
                        if len(sorted_indices) > 0 and scores[sorted_indices[0]] > 0.999:
                            sorted_indices = sorted_indices[1:]
                            
                    start_idx = st.session_state.search_offset
                    end_idx = start_idx + 5
                    top_local_indices = sorted_indices[start_idx:end_idx]

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Display Recommendations
            col_h1, col_h2 = st.columns([4, 1])
            with col_h1:
                st.markdown("### TOP RECOMMENDATIONS")
                if len(top_local_indices) > 0:
                    ui_components.display_vibe_summary(filtered_df.iloc[top_local_indices])
            with col_h2:
                if st.button("Load More", help="Next page"):
                    st.session_state.search_offset += 5
                    st.rerun()

            for local_idx in top_local_indices:
                row = filtered_df.iloc[int(local_idx)]
                score = scores[int(local_idx)].item()
                ui_components.render_song_card(row, score, df_full, song_embeddings_full)

    else:
        st.markdown("""
        <div style='text-align: center; color: #444; margin-top: 80px; border: 2px dashed #222; padding: 40px; border-radius: 12px;'>
            Upload an image in the sidebar to begin analysis.
        </div>
        """, unsafe_allow_html=True)