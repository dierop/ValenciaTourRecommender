import pandas as pd

def cambio_escala(df):
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df['score'] = df['score'].apply(lambda x: 1 + (x -1) * 9 /6 if pd.notnull(x) else x)
    return df
