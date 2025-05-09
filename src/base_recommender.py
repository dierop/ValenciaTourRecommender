from abc import ABC, abstractmethod
from src.data_loader import Data
import numpy as np
import pandas as pd
class BaseRecommender(ABC):

    def __init__(self, data: Data):
        self.data = data
 
    @abstractmethod
    def get_user_preferences(self, user_id):
        pass
    
    def get_items_visited(self, user_id):
        return self.data.puntuaciones[self.data.puntuaciones['user'] == user_id]['place'].values
    
    @abstractmethod
    def get_relevant_items(self, preferences, items_visitados)->pd.DataFrame:
        pass
    
    @abstractmethod
    def compute_scores(self, relevant_items)->pd.DataFrame:
        pass

    def recommend(self, user_id, n=10):
        """
        
        Returns the top n items to recommend to the user_id (id, name, score)
        """
        preferences = self.get_user_preferences(user_id)
        items_visitados = self.get_items_visited(user_id)
        relevant_items = self.get_relevant_items(preferences, items_visitados)
        relevant_items = self.compute_scores(relevant_items)
        items= relevant_items['item'].values[:n]
        scores = relevant_items['score'].values[:n]
        names = self.data.items[self.data.items['item'].isin(items)]['name'].values
        other = relevant_items['other'].values[:n]
        return list(zip(items, names, scores, other))

    