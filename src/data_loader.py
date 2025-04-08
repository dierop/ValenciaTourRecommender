import pandas as pd
from src.preprocess import cambio_escala, get_all_preferences

class DataLoader():


    def load_puntuaciones(self, path: str = "data/puntuaciones_usuario_base.txt") -> pd.DataFrame:
        """
        Load the puntuaciones dataset from the given path.
        """
        return self.update_type(self._load_file(path, ['user','place','score']))
    
    def load_puntuaciones_test(self, path: str = "data/puntuaciones_usuario_test.txt") -> pd.DataFrame:
        """
        Load the puntuaciones dataset from the given path.
        """
        return self.update_type(self._load_file(path, ['user','place','score']))

    
    def load_datos_personales(self, path: str = "data/usuarios_datos_personales.txt") -> pd.DataFrame:
        """
        Load the datos dataset from the given path.
        """
        df = self._load_file(path, ['user','name','age','sex','occupation','children', 'y_c_age','o_c_age'])
        return self.update_type(df, ['user','age','occupation','children', 'y_c_age','o_c_age'])
    
    def load_usuarios_preferencias(self, path: str = "data/usuarios_preferencias.txt") -> pd.DataFrame:
        """
        Load the datos dataset from the given path.
        preferences are of level 1 or 2
        """
        return self.update_type(self._load_file(path, ['user','preference','score']))
    
    def load_ocupaciones(self, path: str = "data/ocupaciones.txt") -> pd.DataFrame:
        """
        Load the datos dataset from the given path.
        """
        return self.update_type(self._load_file(path, ['occupation','name']), ['occupation'])
    
    def load_preferencias(self, path: str = "data/preferencias.txt") -> pd.DataFrame:
        """
        Load the datos dataset from the given path.
        """
        return self.update_type(self._load_file(path, ['preference','name','father']), ['preference','father'])
    
    def load_items(self, path: str = "data/items.txt") -> pd.DataFrame:
        """
        Load the datos dataset from the given path.
        """
        return  self.update_type(self._load_file(path, ['item','name','views']), ['item','views'])
    
    def load_clasificacion_items(self, path: str = "data/clasificacion_items.txt") -> pd.DataFrame:
        """
        Load the datos dataset from the given path.
        """
        return  self.update_type(self._load_file(path, ['item','preference','score']))
    
    def _load_file(self, path: str , columns: list) -> pd.DataFrame:
        """
        Load the puntuaciones dataset from the given path.
        """
        with open(path, "r", encoding='latin1') as f:
            lines = f.readlines()

            # Procesar el archivo en bloques de 3 líneas
            data = [lines[i:i+len(columns)] for i in range(0, len(lines), len(columns))]

            # Convertir a un DataFrame
            df = pd.DataFrame(data, columns=columns)

            # Limpiar los saltos de línea
            df = df.map(lambda x: x.strip())

            # Mostrar el DataFrame
            return df
        
    def update_type(self, df, columns=None, type='int'):
        """
        Update the type of the columns in the DataFrame
        """
        if columns is None:
            columns = df.columns
        for column in columns:
            df[column] = df[column].astype(type)
        return df

class Data():
    def __init__(self):
        self.loader= DataLoader()
        self.preferences = self.loader.load_preferencias()
        self.users = self.loader.load_usuarios_preferencias()
        self.items = self.loader.load_items()
        self.clasificacion_items = self.loader.load_clasificacion_items()
        self.puntuaciones = self.loader.load_puntuaciones()
        self.datos_personales = self.loader.load_datos_personales()
        self.ocupaciones = self.loader.load_ocupaciones()
        self.puntuaciones_test = self.loader.load_puntuaciones_test()
        self.all_preferences, self.user_mapping = get_all_preferences(self.preferences, self.users)



