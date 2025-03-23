from preprocess import get_all_preferences
from data_loader import DataLoader
class BaseRecommender():

    def __init__(self):
        loader= DataLoader()
        df_preferences = loader.load_preferencias()
        df_users = loader.load_usuarios_preferencias()
        self.all_preferences, self.user_mapping = get_all_preferences(df_preferences, df_users)
        self.items = loader.load_items()
        self.clasificacion_items = loader.load_clasificacion_items()
        self.puntucaiones = loader.load_puntuaciones()

    def get_user_preferences(self, user_id):
        user_idx = self.user_mapping[user_id]
        return self.all_preferences[user_idx]
    
    def get_relevant_items(self, user_id):
        preferences = self.get_user_preferences(user_id)
        items_visitados = self.puntucaiones[self.puntucaiones['user'] == user_id]['place'].values
        items = []
        for i, score in enumerate(preferences):
            if score > 0:
                item_id = self.items.iloc[i]['item']
                items.append((item_id, score))

    def recommend(self, user_id, n=10):
        user_idx = self.user_mapping[user_id]
        scores = self.model.predict(user_idx, np.arange(len(self.item_mapping)))
        scores = np.array(scores)
        scores = scores.squeeze()
        best = np.argsort(scores)[::-1]
        return [(self.item_mapping[i], scores[i]) for i in best[:n]]
    