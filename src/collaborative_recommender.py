from src.base_recommender import BaseRecommender
from src.data_loader import Data
from src.assing_group import asignar_grupos
import pandas as pd
import numpy as np
from collections import defaultdict
from src.preprocess import get_neighbours


class CollaborativeRecommender(BaseRecommender):

    def __init__(self, data: Data = Data(), vecinos=20):
        super().__init__(data)
        self.vecinos = vecinos


    def get_user_preferences(self, user_id):

        neighbours = get_neighbours(self.data.users, self.vecinos)

        user_neighbours = neighbours[neighbours['user_id'] == user_id]

        return list(zip(user_neighbours['vecinos'][0], user_neighbours['pearson'][0]))


    def get_relevant_items(self, preferences, items_visitados):
        relevant = []
        for v,cp in preferences:
            v_puntuaciones = self.data.puntuaciones[self.data.puntuaciones['user'] == v]
            v_puntuaciones = v_puntuaciones[~v_puntuaciones['place'].isin(items_visitados)]

            # get top 5 items
            v_puntuaciones = v_puntuaciones.sort_values('score', ascending=False).head(5)
            items = v_puntuaciones['place'].values
            scores = v_puntuaciones['score'].values

            for i, score in zip(items, scores):


                views = self.data.items[self.data.items['item'] == i]['views'].values[0]
                relevant.append(
                    {'item': i,
                    'score1': cp,
                    'score2': score,
                    'views': views,
                    'other': v
                    })
        return pd.DataFrame(data=relevant)

    def compute_scores(self, relevant_items):
        for item, group in relevant_items.groupby('item'):
            relevant_items.loc[relevant_items['item'] == item, 'score'] = (group['score1'] * group['score2']).sum()
            relevant_items.loc[relevant_items['item'] == item, 'other'] =  len(group)

        relevant_items = relevant_items.sort_values('score', ascending=False)
        relevant_items = relevant_items.drop_duplicates(subset=['item'], keep='first')
        max_score = relevant_items['score'].max()
        if max_score != 0:
            factor = 10 / max_score
            relevant_items['score'] = relevant_items['score'] * factor
        return relevant_items

