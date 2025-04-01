from src.base_recommender import BaseRecommender
from src.data_loader import DataLoader

def recommender_evaluation(recommender:BaseRecommender, top_k: int):
    dl = DataLoader()
    test=dl.load_puntuaciones_test()
    test = test.sort_values("score",ascending=False)
    precision=[]
    # print(f"Evaluacion de { len(test.groupby("user"))} usuarios")
    for usr,group in test.groupby("user"):
        rec = recommender.recommend(
                user_id=usr,
                n=top_k,
            )
        # print(rec)
        # print([item[0] for item in rec])
        
        base_top=list(group["place"][:top_k])
        # print(base_top)

        relevantes_en_top_K = len([item[0] for item in rec if item[0] in base_top])
        precision_at_K = relevantes_en_top_K / top_k
        precision.append(precision_at_K)
        # print([item[0] for item in rec if item[0] in base_top])
        
    print(f"Precisión de cada usuario: {precision}")
    ac = sum(precision)/len(test.groupby("user"))

    print(f"Accuracy top {top_k}: {ac*100}%")