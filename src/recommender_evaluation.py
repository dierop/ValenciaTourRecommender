from src.content_recommender import ContentRecommender
from src.demographic_recommender import DemographicRecommender
from src.collaborative_recommender import CollaborativeRecommender
from src.hybrid_recommender import HybridRecommender
from src.data_loader import Data
from typing import List, Tuple

class RecommenderEvaluation():

    def __init__(self, data: Data = Data(), cr: ContentRecommender = None, dr: DemographicRecommender = None, cor: CollaborativeRecommender = None, hr: HybridRecommender = None):
        self.cr = cr if cr is not None else ContentRecommender(data)
        self.dr = dr if dr is not None else DemographicRecommender(data)
        self.cor = cor if cor is not None else CollaborativeRecommender(data)
        self.hr = hr if hr is not None else HybridRecommender(data, cr, dr, cor)
        self.data = data
        self.test_users = self.get_best_test_users()
        self.max_rec = 30
    
    def get_best_test_users(self, n: int = 20) -> List[int]:
        """
        Devuelve una lista de los mejores usuarios para el test.
        """
        # Obtener los usuarios con más interacciones
    #     return (
    #     self.data.puntuaciones_test['user']   # Serie de usuarios
    #     .value_counts()                       # Series: índice=user, valor=nº interacciones
    #     .head(n)                              # primeros n
    #     .index                                 
    #     .tolist()
    # )
        return (
            self.data.puntuaciones_test[self.data.puntuaciones_test["score"] > 2]                    # 1️⃣ Filtra por score > 2
            .groupby("user")                       # 2️⃣ Agrupa por usuario
            .size()                                # 3️⃣ Cuenta filas en cada grupo
            .sort_values(ascending=False)          # 4️⃣ Ordena de mayor a menor
            .head(n)                               # 5️⃣ Top‑n
            .index
            .tolist()                              # 6️⃣ Devuelve solo los IDs
        )

    def evaluate_recommender(self, user_id:int,rec,umbral_rec:int, umbral_real:int, weigths = None,) -> Tuple[float, float, float, float]:

        """
        Devuelve las métricas de un recomendador.
        """
        if isinstance(rec, HybridRecommender):
            # Si el recomendador es híbrido, se necesita la lista de usuarios
            recomendaciones = rec.recommend(user_id, self.max_rec, weigths)
        else:
            recomendaciones = rec.recommend(user_id, self.max_rec)
        
        # Obtener las recomendaciones y las puntuaciones reales
        rec_items = [(item[0], item[2]) for item in recomendaciones if item[2] >= umbral_rec]
        real_items = self.data.puntuaciones_test[self.data.puntuaciones_test["user"] == user_id][["place", "score"]].values.tolist()
        # unpack metrics
        precision, recall, f1 = self.get_metrics(rec_items, real_items, umbral_real)

        if precision == 0 and recall == 0:
            print(f"For user {user_id} in {rec.__class__.__name__} no hay metricas")
            print(f"Rec: {rec_items}")
            print(f"Real: {real_items}")

        return precision, recall, f1, self.get_mae(rec_items, real_items)


    def get_metrics(self, rec:List, real:List, umbral_real:float) -> Tuple[float, float, float]:
        """
        Devuelve las métricas de precisión y recall.
        """
        # Convertir a conjuntos para facilitar la comparación
              # 0.7

        rec_set = set(item[0] for item in rec)
        real_set = set((item[0]) for item in real if item[1] >= umbral_real)

        # Calcular precisión y recall
        tp = len(rec_set.intersection(real_set))
        precision = tp / len(rec_set) if len(rec_set) > 0 else 0
        recall = tp / len(real_set) if len(real_set) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        

        return precision, recall, f1
    
    def get_mae(self, rec:List, real:List) -> float:
        """
        Devuelve el MAE.
        """
        # Convertir a conjuntos para facilitar la comparación
        MAX_REAL = 7
        MAX_PRED = 10
        factor = MAX_REAL / MAX_PRED 
        rec_set = set(rec)
        if len(rec_set) == 0:
            # print(rec,real)
            return 1
        real_dic = {item[0]: item[1] for item in real}
        mae = 0
        for item_id, score in rec_set:
            mae += abs(score* factor - real_dic.get(item_id, 0))
        mae /= len(rec_set) if len(rec_set) > 0 else 0

        return mae
    
    def evaluate_all_recommenders(self, user_id:int, umbral_rec:float, umbral_real:float, hybrid_weigths=[1,1,1], exploration=False) -> dict:
        """
        Devuelve las métricas de todos los recomendadores.
        """
        results = {}
        for rec in [self.dr, self.cr, self.cor, self.hr] if not exploration else [self.hr]:
            precision, recall, f1, mae = self.evaluate_recommender(user_id, rec, umbral_rec, umbral_real, hybrid_weigths)
            results[rec.__class__.__name__] = {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "mae": mae
            }
        return results
    
    def evaluate_all_users(self, umbral_rec:float, umbral_real:float, hybrid_weigths=[1,1,1], exploration=False) -> dict:
        """
        Devuelve las métricas de todos los recomendadores para todos los usuarios.
        """
        results = {}
        for user_id in self.test_users:
            results[user_id] = self.evaluate_all_recommenders(user_id, umbral_rec, umbral_real, hybrid_weigths, exploration)
        return results
    
    def evaluate_all_users_aggregated(self, all_user_result:dict) -> dict:
        """
        Devuelve las métricas de todos los recomendadores para todos los usuarios.
        """

        results = {}
        for _, recs in all_user_result.items():
            for rec_name, metrics in recs.items():
                if rec_name not in results:
                    results[rec_name] = {
                        "precision": 0,
                        "recall": 0,
                        "f1": 0,
                        "mae": 0
                    }
                results[rec_name]["precision"] += metrics["precision"]
                results[rec_name]["recall"] += metrics["recall"]
                results[rec_name]["f1"] += metrics["f1"]
                results[rec_name]["mae"] += metrics["mae"]
        
        # Promediar los resultados
        for rec_name, metrics in results.items():
            for metric, value in metrics.items():
                metrics[metric] = value / len(self.test_users)
        
        return results
    