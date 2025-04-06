from src.base_recommender import BaseRecommender
from src.data_loader import Data
import pandas as pd
import numpy as np
from collections import defaultdict
from src.preprocess import get_all_preferences

class ContentRecommender(BaseRecommender):

    def __init__(self, data: Data = Data()):
        super().__init__(data)
        self.clasificacion_items = data.clasificacion_items.groupby('preference')
        self.clasificacion_items_keys = list(self.clasificacion_items.groups.keys())


 
    def get_user_preferences(self, user_id):
        if not user_id in self.data.user_mapping:
            # recomput user preferences
            self.data.user_mapping, self.data.all_preferences = get_all_preferences(self.data.preferences, self.data.users)
        user_index = self.data.user_mapping[user_id]
        user_preferences = self.data.all_preferences[user_index]

        return user_preferences


    
    def get_relevant_items(self, preferences, items_visitados):
        relevant = []
        for i, score in enumerate(preferences):
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
                        'other': None
                        })
        return pd.DataFrame(data=relevant)
    
    def compute_scores(self, relevant_items):
        relevant_items['score'] = 5/10*relevant_items['score1'] + 3/100*relevant_items['score2'] + 2/38* relevant_items['views']
        relevant_items = relevant_items.sort_values('score', ascending=False)
        return relevant_items.drop_duplicates(subset='item', keep='first')
