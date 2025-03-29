import numpy as np

def get_group_preferences(df_merged, all_preferences, user_map, assign_group_fn):
    """
    Calcula las preferencias promedio por grupo. Cada usuario puede estar en varios grupos.
    """
    from collections import defaultdict
    import numpy as np

    group_vectors = defaultdict(list)

    for _, row in df_merged.iterrows():
        user_id = row['user_id']
        grupos = assign_group_fn(row)  

        if user_id in user_map:
            user_idx = user_map[user_id]
            user_pref_vector = all_preferences[user_idx]

            for grupo in grupos:
                group_vectors[grupo].append(user_pref_vector)

    group_means = {}
    for grupo, vectors in group_vectors.items():
        group_array = np.vstack(vectors)
        group_means[grupo] = np.round(group_array.mean(axis=0), 2)

    return group_means

def recomendar_por_grupo(usuario, group_preferences, assign_group_fn):
    """
    Retorna un vector de preferencias promedio para un usuario basado en sus grupos demográficos.
    """
    grupos = assign_group_fn(usuario)
    vectores = []

    for grupo in grupos:
        if grupo in group_preferences:
            vectores.append(group_preferences[grupo])

    if not vectores:
        return np.zeros_like(next(iter(group_preferences.values())))
    
    return np.mean(np.vstack(vectores), axis=0)