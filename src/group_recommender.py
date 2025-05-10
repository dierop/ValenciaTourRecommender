from src.content_recommender import ContentRecommender
from src.demographic_recommender import DemographicRecommender
from src.collaborative_recommender import CollaborativeRecommender
from src.hybrid_recommender import HybridRecommender
from src.data_loader import Data
import pandas as pd
from collections import defaultdict
from typing import List, Tuple

class GroupRecommender():

    def __init__(self, data: Data = Data(), cr: ContentRecommender = None, dr: DemographicRecommender = None, cor: CollaborativeRecommender = None, hr: HybridRecommender = None):
        self.cr = cr if cr is not None else ContentRecommender(data)
        self.dr = dr if dr is not None else DemographicRecommender(data)
        self.cor = cor if cor is not None else CollaborativeRecommender(data)
        self.hr = hr if hr is not None else HybridRecommender(data, cr, dr, cor)
        self.data = data
        # self.weights = [0.3, 0.3, 0.4]  # [demográfica, contenido, colaborativa] pesos iniciales



    def group_recommend(
        self,
        users_id: List[int],
        types       = (1, 1, 1, 1),   # activar/desactivar módulos
        checks      = (1, 1, 1),      # flags para el híbrido
        n: int = 5          # tamaño de la lista grupal
    ) -> List[Tuple[int, str, float, int]]:
        """
        Devuelve m ítems como (item_id, name, proporción, rank_sum).
        """
        # ----------- 1. Recomendaciones individuales ------------------
        usuario_tops = {}                # user_id -> lista (item_id, name, rank, score)
        total_users  = len(users_id)

        per_user_k = max(10,n)

        for user in users_id:
            rec_lists = [
                self.dr.recommend(user, per_user_k)         if types[0] else None,
                self.cr.recommend(user, per_user_k)         if types[1] else None,
                self.cor.recommend(user, per_user_k)        if types[2] else None,
                self.hr.recommend(user, per_user_k, checks) if types[3] else None,
            ]

            scores = defaultdict(float)       # item -> score acumulado
            names  = {}                       # item -> name

            for rec in rec_lists:
                if rec is None:
                    continue
                # cada rec es lista de (item_id, name, score)
                for item_id, name, score,_ in rec:
                    scores[item_id] += score
                    names.setdefault(item_id, name)

            if not scores:
                continue
            
            top_k = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:per_user_k]
            usuario_tops[user] = [
                (item_id, names[item_id], rank + 1, score)
                for rank, (item_id, score) in enumerate(top_k)
            ]

        if not usuario_tops:          # ningún usuario produce recomendación
            return []

        # ----------- 2. Agregación grupal -----------------------------
        rank_sum   = defaultdict(int)     # item -> suma de rankings
        count_user = defaultdict(int)     # item -> nº usuarios que lo incluyen
        item_name  = {}                   # item -> name

        for ranked_list in usuario_tops.values():
            for item_id, name, rank, _ in ranked_list:
                rank_sum[item_id]   += rank
                count_user[item_id] += 1
                item_name[item_id]   = name

        # proporción de usuarios que lo quieren
        prop = {item: cnt / total_users for item, cnt in count_user.items()}

        # ordenar: 1º proporción desc, 2º rank_sum asc, 3º item_id
        ordering = sorted(
            prop.keys(),
            key=lambda it: (-prop[it], rank_sum[it], it)
        )[:n]

        return [
            (it, item_name[it], prop[it], rank_sum[it])
            for it in ordering
        ]