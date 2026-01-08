import pandas as pd
import pickle
import requests
import time
from tqdm import tqdm 

INPUT_FILE = 'songs_with_embeddings.pkl'
OUTPUT_FILE = 'songs_enriched.pkl'

def fetch_itunes_metadata(artist, track_name):
    try:
        base_url = "https://itunes.apple.com/search"
        params = {
            'term': f"{artist} {track_name}",
            'media': 'music',
            'entity': 'song',
            'limit': 1
        }
        response = requests.get(base_url, params=params, timeout=3)
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            if results:
                track = results[0]
                return {
                    'genre': track.get('primaryGenreName', 'Unknown'),
                    'year': track.get('releaseDate', '2000')[:4], 
                    'preview': track.get('previewUrl'),
                    'image': track.get('artworkUrl100').replace('100x100bb', '600x600bb')
                }
    except Exception as e:
        pass
    
    return None

def main():
    print(f"Loading {INPUT_FILE}...")
    with open(INPUT_FILE, 'rb') as f:
        data = pickle.load(f)
    
    df = data['df']
    embeddings = data['embeddings']
    
    if 'genre' not in df.columns:
        df['genre'] = 'Unknown'
    if 'year' not in df.columns:
        df['year'] = 0
    if 'preview_url' not in df.columns:
        df['preview_url'] = None
    if 'album_art' not in df.columns:
        df['album_art'] = None

    df = df.copy()
    for index, row in tqdm(df.iterrows(), total=len(df)):
        metadata = fetch_itunes_metadata(row['artist'], row['name'])
        
        if metadata:
            df.at[index, 'genre'] = metadata['genre']
            try:
                df.at[index, 'year'] = int(metadata['year'])
            except:
                df.at[index, 'year'] = 2000
                
            df.at[index, 'preview_url'] = metadata['preview']
            df.at[index, 'album_art'] = metadata['image']
        else:
            if df.at[index, 'genre'] == 'Unknown':
                df.at[index, 'genre'] = 'Pop' # default
            if df.at[index, 'year'] == 0:
                df.at[index, 'year'] = 2020

        time.sleep(0.05)
    
    new_data = {
        'df': df,
        'embeddings': embeddings
    }
    
    with open(OUTPUT_FILE, 'wb') as f:
        pickle.dump(new_data, f)
        
    print(f"saved data to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()