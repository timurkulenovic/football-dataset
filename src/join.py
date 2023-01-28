import os

import pandas as pd

league = "ligue_1"
dir_path = f"../data/{league}/games"

frames = []
for file_path in sorted(os.listdir(os.path.join(dir_path, "seasons"))):
    df = pd.read_csv(os.path.join(dir_path, "seasons", file_path))
    frames.append(df)

df = pd.concat(frames, ignore_index=True)
df.columns = [col.upper() for col in df.columns]
df.to_csv(os.path.join(dir_path, "games.csv"), index=False)

