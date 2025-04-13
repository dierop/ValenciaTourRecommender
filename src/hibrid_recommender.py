
from src.content_recommender import ContentRecommender
from src.demographic_recommender import DemographicRecommender
from src.base_recommender import BaseRecommender
from src.data_loader import Data
import pandas as pd
import numpy as np

class HibridRecommender():

    def __init__(self, data: Data = Data(), cr:ContentRecommender = None, dr:DemographicRecommender = None, cor: BaseRecommender = None):
        
        self.cr = cr if cr is not None else ContentRecommender(data)
        self.dr = dr if dr is not None else DemographicRecommender(data)
        
        self.cor = cor
        self.data = data
        self.weights = [0.3,0.3,0.4]

    
    def update_weigths(self, user_id, weights, checks=[1,1,1]):
        """
        Update the weights of the recommender system dinamically if theer is no user info for the recommendation
        """
        pesos_ajustados  = weights

        # check DemographicRecommender
        pesos_ajustados[0] = 0 if self.data.datos_personales[self.data.datos_personales["user"]==user_id].empty or not checks[0] else pesos_ajustados[0]

        # check ContentRecommender
        pesos_ajustados[1] = 0 if not user_id in self.data.user_mapping or not checks[1] else pesos_ajustados[1]
        
        suma_pesos = sum(pesos_ajustados)
            
        pesos_normalizados = [
            peso / suma_pesos if peso > 0 else 0.0
            for peso in pesos_ajustados
        ]


        return pesos_normalizados
    
    def compute_scores(self, relevant_items , pesos):
        """
        Compute the scores of the items
        """
        dict_item_score = {}
        
        for df, w in zip(relevant_items, pesos):
            if w==0:
                continue
            else:
                for _, row in df.iterrows():
                    item = row['item']
                    score = row['score']
                    
                    # Calculamos la parte correspondiente al peso
                    contribucion = score * w
                    
                    # Acumulamos en el diccionario
                    if item not in dict_item_score:
                        dict_item_score[item] = contribucion
                        names = self.data.items[self.data.items['item'].isin(items)]['name'].values
                        other = relevant_items['other'].values[:n]
                    else:
                        dict_item_score[item] += contribucion
