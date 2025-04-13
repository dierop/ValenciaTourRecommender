from src.base_recommender import BaseRecommender
from src.data_loader import Data
from src.assing_group import asignar_grupos
import pandas as pd
import numpy as np
from collections import defaultdict
from src.preprocess import merge_userdata_ocupacion
from src.preprocess import get_neighbours


class CollaborativeRecommender(BaseRecommender):

    def __init__(self, data: Data = Data()):
        super().__init__(data)
        self.clasificacion_items = data.clasificacion_items.groupby('preference')
        self.clasificacion_items_keys = list(self.clasificacion_items.groups.keys())
        self.group_preferences  = self._get_group_preferences()

 
    def get_user_preferences(self, user_id):
        return 
    
    
    def get_relevant_items(self, preferences, items_visitados):
        relevant = []
        for p,group in preferences:
            for i, score in enumerate(p):
                # If the preference is not in the clasificacion_items, skip it
                if i not in self.clasificacion_items_keys:
                    continue
                
                # If the score is 0, skip it
                if score > 0:
                    pref_items = self.clasificacion_items.get_group(i)
                    pref_items = pref_items[~pref_items['item'].isin(items_visitados)]
                    
                    for i in range(len(pref_items)):
                        item_id = pref_items.iloc[i]['item']
                        views = self.data.items[self.data.items['item'] == item_id]['views'].values[0]
                        relevant.append(
                            {'item': item_id,
                            'score1': score,
                            'score2': pref_items.iloc[i]['score'],
                            'views': views,
                            'other': group
                            })
        return pd.DataFrame(data=relevant)
    
    def compute_scores(self, relevant_items):
        relevant_items['score'] = 5/10*relevant_items['score1'] + 3/100*relevant_items['score2'] + 2/38* relevant_items['views']
        relevant_items = relevant_items.sort_values('score', ascending=False)
        return relevant_items.drop_duplicates(subset='item', keep='first')
        

    def _get_group_preferences(self):
        """
        Calcula las preferencias promedio por grupo. Cada usuario puede estar en varios grupos.
        """

        group_vectors = defaultdict(list)

        for _, row in merge_userdata_ocupacion(self.data.datos_personales,self.data.ocupaciones).iterrows():
            user_id = row['user_id']
            grupos = asignar_grupos(row)  

            if user_id in self.data.user_mapping:
                user_idx = self.data.user_mapping[user_id]
                user_pref_vector = self.data.all_preferences[user_idx]

                for grupo in grupos:
                    group_vectors[grupo].append(user_pref_vector)

        group_means = {}
        for grupo, vectors in group_vectors.items():
            group_array = np.vstack(vectors)
            group_means[grupo] = np.round(group_array.mean(axis=0), 2)

        return group_means
    