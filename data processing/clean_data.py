import pandas as pd
import os

input_file = 'spotify_dataset_10k.csv'
output_file = 'cleaned_songs.csv'

if not os.path.exists(input_file):
    print(f"Error: Could not find '{input_file}' in this folder.")
    exit()

df = pd.read_csv(input_file)

required_columns = {
    'track_id': 'id',
    'track_name': 'name',
    'artists': 'artist',
    'energy': 'energy',
    'valence': 'valence',
    'acousticness': 'acousticness',
    'danceability': 'danceability',
    'tempo': 'tempo'
}

try:
    df_clean = df[list(required_columns.keys())].rename(columns=required_columns)
except KeyError as e:
    print(f"Error: CSV is missing a required column = {e}")
    print("Columns = ", list(df.columns))
    exit()

df_clean.dropna(inplace=True)
df_clean.drop_duplicates(subset=['id'], inplace=True)
df_clean = df_clean.head(10000)

df_clean.to_csv(output_file, index=False)
print(f"Saved {len(df_clean)} songs to '{output_file}'")