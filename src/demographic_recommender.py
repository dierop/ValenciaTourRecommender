from src.base_recommender import BaseRecommender
from src.data_loader import Data
import pandas as pd
class DemographicRecommender(BaseRecommender):

    def __init__(self, data: Data = Data()):
        super().__init__(data)
        self.clasificacion_items = data.clasificacion_items.groupby('preference')
        self.clasificacion_items_keys = list(self.clasificacion_items.groups.keys())
 
    def get_user_preferences(self, user_id):
        return self.data.all_preferences[user_id]
    
    
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
                         'views': views})
        return pd.DataFrame(data=relevant, columns=['item', 'score1', 'score2', 'views'])
    
    def compute_scores(self, relevant_items):
        relevant_items['score'] = relevant_items['score1'] * relevant_items['score2'] * relevant_items['views']
        return relevant_items.sort_values('score', ascending=False)
    