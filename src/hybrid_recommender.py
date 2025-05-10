from src.content_recommender import ContentRecommender
from src.demographic_recommender import DemographicRecommender
from src.base_recommender import BaseRecommender
from src.data_loader import Data
import pandas as pd
import numpy as np

class HybridRecommender():

    def __init__(self, data: Data = Data(), cr: ContentRecommender = None, dr: DemographicRecommender = None, cor: BaseRecommender = None):
        self.cr = cr if cr is not None else ContentRecommender(data)
        self.dr = dr if dr is not None else DemographicRecommender(data)
        self.cor = cor
        self.data = data
        self.weights = [0.3, 0.3, 0.4]  # [demográfica, contenido, colaborativa] pesos iniciales

    def update_weights(self, user_id, weights, checks=[1, 1, 1]):
        pesos_ajustados = weights.copy()

        # Validar disponibilidad de datos
        if self.data.datos_personales[self.data.datos_personales["user"] == user_id].empty or not checks[0]:
            pesos_ajustados[0] = 0
        if user_id not in self.data.user_mapping or not checks[1]:
            pesos_ajustados[1] = 0
        if self.cor is None or not checks[2]: #cambiar cuando se tenga colaborativa
            pesos_ajustados[2] = 0

        suma = sum(pesos_ajustados)
        return [w / suma if suma > 0 else 0 for w in pesos_ajustados]

    def compute_scores(self, item_lists, weights):
        scores = {}

        for data, weight in zip(item_lists, weights):
            if weight == 0 or data is None:
                continue

            if isinstance(data, list):
                data = [(item[0], item[2]) for item in data]
                data = pd.DataFrame(data, columns=["item", "score"])    

            for _, row in data.iterrows():
                item = row['item']
                score = row['score'] * weight
                scores[item] = scores.get(item, 0) + score

        return scores

    def recommend(self, user_id, n=10, checks=[1, 1, 1]):
        """
        checks: [demográfica, contenido, colaborativa]
        """
        # 0. Devolver lo mismo si solo hay un recomendador activo
        # if sum(checks) == 1:
        #     if checks[0]: return self.dr.recommend(user_id, n)
        #     if checks[1]: return self.cr.recommend(user_id, n)
        #     if checks[2] and self.cor is not None: return self.cor.recommend(user_id, n)

        # 1. Obtener recomendaciones
        demograficas = self.dr.recommend(user_id, n) if checks[0] else None
        contenido = self.cr.recommend(user_id, n) if checks[1] else None
        colaborativas = self.cor.recommend(user_id, n) if checks[2] and self.cor is not None else None

        # 2. Actualizar pesos
        pesos = self.update_weights(user_id, self.weights, checks)

        # 3. Combinar recomendaciones
        scores = self.compute_scores([demograficas, contenido, colaborativas], pesos)

        # 4. Ordenar por score y devolvemos los top N
        recomendaciones_ordenadas = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]

        # 5. Obtener nombres desde el dataset
        resultados = pd.DataFrame(recomendaciones_ordenadas, columns=["item", "score"])
        resultados = resultados.merge(self.data.items, on="item", how="left")

        # 6. Mismo formato 
        resultado_final = [
            (int(row["item"]), row["name"], float(row["score"]), None)
            for _, row in resultados.iterrows()
        ]

        return resultado_final