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
        self.hr = hr if hr is not None else HybridRecommender(data)
        self.data = data
        # self.weights = [0.3, 0.3, 0.4]  # [demográfica, contenido, colaborativa] pesos iniciales


    def recommend(
        self,
        users_ids: List[int],
        types=(1, 1, 1, 1),     # demográfica, contenido, colaborativa, híbrida
        checks=(1, 1, 1),       # flags para el híbrido
        n: int = 5
    ) -> List[Tuple[int, str, int]]:
        """
        TOP-5 grupal: se suma el ranking 1..5 de cada usuario
        y se conservan id y name de cada ítem.
        """
        # ---------- 1. TOP-n por usuario --------------------------------
        top_por_usuario = {}   # user_id -> list[(item_id, name, rank_pos, score_sum)]

        for user in users_ids:
            # Llama a cada recomendador activo
            rec_lists = [
                self.dr.recommend(user, n)         if types[0] else None,
                self.cr.recommend(user, n)         if types[1] else None,
                self.cor.recommend(user, n)        if types[2] else None,
                self.hr.recommend(user, n, checks) if types[3] else None,
            ]

            # Acumula scores por item_id
            scores = defaultdict(float)        # item_id -> score_sum
            names  = {}                        # item_id -> name (tal cual del 1er sistema)

            for rec in rec_lists:
                if rec is None:
                    continue

                # estándar: lista de (id, name, score)
                for item_id, name, score,_ in rec:
                    scores[item_id] += score
                    names.setdefault(item_id, name)   # conserva el primero

            if not scores:
                continue

            # Ordena por score y coge el TOP-n para ese usuario
            ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]
            ranked = [
                (item_id, names[item_id], rank + 1, score)    # rank es 1..n
                for rank, (item_id, score) in enumerate(ranked)
            ]
            top_por_usuario[user] = ranked

        # ---------- 2. Agregación de rankings ---------------------------
        rank_sum = defaultdict(int)         # item_id -> suma de rankings
        item_name = {}                      # item_id -> name (cualquiera)

        for ranked_list in top_por_usuario.values():
            for item_id, name, rank, _score in ranked_list:
                rank_sum[item_id] += rank
                item_name[item_id] = name

        if not rank_sum:      # ningún ítem recomendado
            return []

        # ---------- 3. TOP-5 grupal por ranking acumulado ---------------
        group_top = sorted(rank_sum.items(), key=lambda x: (x[1], x[0]))[:n]
        return [(item_id, item_name[item_id], rank_sum[item_id],'') for item_id, _ in group_top]
    

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

        per_user_k = max(10,n*2)

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