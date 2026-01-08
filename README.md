# PixelPlay: Image to Audio Translation Engine 

**PixelPlay** is a multimodal AI application that translates visual stimuli (images) into auditory experiences (songs). It uses Computer Vision and Vector Embeddings to bridge the gap between sight and sound.

 **Live Demo:** https://pixelplay-demo.streamlit.app/

---

## How It Works

PixelPlay does not use simple tag matching. It uses **Cross-Modal Vector Embeddings** to understand the "vibe" of an image mathematically.

1.  **Visual Encoder:** The app uses OpenAI's **CLIP (Contrastive Language-Image Pretraining)** model to convert an uploaded image into a 512-dimensional vector.
2.  **Audio Vector Space:** I preprocessed a dataset of 10,000 songs, generating text descriptions for each and converting them into the same vector space.
3.  **Cosine Similarity Search:** When you upload an image, the app calculates the cosine similarity between the **Image Vector** and every **Song Vector** in the database to find the closest semantic matches.

### Key Features
* **Multimodal Search:** Search for music using Images, Text, or a combination of both (Hybrid Search).
* **Pivot Search:** "Find Similar" feature allows users to pivot from visual search to audio-based vector search.
* **Audio Intelligence:** Visualizes song metrics (Energy, Valence, Danceability) using Radar Charts.
* **Secure Authentication:** Includes user registration, password hashing (bcrypt), and session management.

---

## Technical Architecture

The repository is structured to separate the **Live Application** from the **Data Engineering Pipeline**.

### 1. The Application (`/`)
* `app.py`: Main Streamlit controller.
* `logic.py`: Handles CLIP model inference and vector calculations.
* `ui_components.py`: Manages the CSS design system and frontend rendering.
* `auth_manager.py`: Handles user session security.

### 2. The Data Pipeline (`/data processing`)
* `clean_data.py`: Pre-processing raw CSV data.
* `embed_songs.py`: Generates vector embeddings for the music dataset using CLIP.
* `enrich_data.py`: Hydrates the dataset with real metadata (Album Art, Preview URLs) via the iTunes API.

### 3. The Data (`/data`)
* Contains the raw source datasets used to build the vector database.

---

## How to Run Locally

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/PixelPlay.git](https://github.com/yourusername/PixelPlay.git)
    cd PixelPlay
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App**
    ```bash
    streamlit run app.py
    ```

---

*Note: This project is a portfolio demonstration. User accounts created in the live demo are ephemeral and may be reset during updates.*
