import pandas as pd
import numpy as np

def cambio_escala(df):
    """"
    Transformacion lineal de 1 al 7 a 0 al 10
    """
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df['score'] = df['score'].apply(lambda x: np.round((x -1) * 10 /6, 2) if pd.notnull(x) else x)
    return df

def get_all_preferences(df_preferences, df_users):

    users = df_users['user'].unique()
    
    # Mapeo de usuarios y preferencias a índices
    user_map = {user: i for i, user in enumerate(users)}

    all_preferences = np.zeros((len(users), len(df_preferences['preference'].unique())+1))

    # Agrupar las preferencias por usuario
    grouped = df_users.sort_values('preference', ascending=True).groupby('user')

    for user, prefs in grouped:
        i = user_map[user]
        for _, row in prefs.iterrows():
            pref = row['preference']
            score = row['score']
            father = df_preferences[df_preferences['preference'] == pref]['father'].values[0]
            if father == 0:
                all_preferences[i, pref] = score
            else:
                father_score = all_preferences[i, father]
                all_preferences[i, pref] = (father_score + score) / 2 if father_score > 0 else score

    return all_preferences, user_map


def merge_userdata_ocupacion(datos_personales, occupacion):
    df_merged = datos_personales.merge(occupacion, on='occupation', how='left', suffixes=('', '_ocuppation'))
    df_merged.rename(columns={'user': 'user_id','name_ocuppation': 'occupation', 'occupation': 'id_occupation', 'y_c_age': 'young_children_age', 'o_c_age': 'older_children_age'}, inplace=True)

    return df_merged