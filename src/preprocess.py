import pandas as pd
import numpy as np

def cambio_escala(df):
    """"
    Transformacion lineal de 1 al 7 a 0 al 10
    """
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df['score'] = df['score'].apply(lambda x: np.round((x -1) * 10 /6, 2) if pd.notnull(x) else x)
    return df
