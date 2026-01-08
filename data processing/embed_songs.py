import pandas as pd
from sentence_transformers import SentenceTransformer
import pickle

df = pd.read_csv('cleaned_songs.csv')

if 'album_art' not in df.columns:
    df['album_art'] = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/12in-Vinyl-LP-Record-Angle.jpg/640px-12in-Vinyl-LP-Record-Angle.jpg"

def create_caption(row):
    if row['energy'] > 0.8:
        energy_desc = "high energy, intense, explosive"
    elif row['energy'] > 0.5:
        energy_desc = "upbeat, lively"
    else:
        energy_desc = "calm, relaxed, low energy"

    if row['valence'] > 0.8:
        mood_desc = "happy, cheerful, euphoric"
    elif row['valence'] > 0.5:
        mood_desc = "neutral, pleasant"
    else:
        mood_desc = "sad, melancholic, dark"

    if row['tempo'] > 120:
        speed_desc = "fast-paced"
    else:
        speed_desc = "slow-paced"

    caption = f"A {mood_desc}, {energy_desc}, {speed_desc} song by {row['artist']}."
    return caption

df['text_description'] = df.apply(create_caption, axis=1)

model = SentenceTransformer('clip-ViT-B-32')
embeddings = model.encode(df['text_description'].tolist(), show_progress_bar=True)

with open('songs_with_embeddings.pkl', 'wb') as f:
    pickle.dump({'df': df, 'embeddings': embeddings}, f)

print("Embeddings saved to 'songs_with_embeddings.pkl'")