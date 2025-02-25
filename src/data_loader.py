import pandas as pd

class DataLoader():


    def load_puntuaciones(self, path: str = "data/puntuaciones_usuario_base.txt") -> pd.DataFrame:
        """
        Load the puntuaciones dataset from the given path.
        """
        return self._load_file(path, ['user','place','score'])
    
    def load_puntuaciones_test(self, path: str = "data/puntuaciones_usuario_test.txt") -> pd.DataFrame:
        """
        Load the puntuaciones dataset from the given path.
        """
        return self._load_file(path, ['user','place','score'])

    
    def load_datos_personales(self, path: str = "data/usuarios_datos_personales.txt") -> pd.DataFrame:
        """
        Load the datos dataset from the given path.
        """
        return self._load_file(path, ['user','name','age','sex','occupation','children', 'y_c_age','o_c_age'])
    
    def load_usuarios_preferencias(self, path: str = "data/usuarios_preferencias.txt") -> pd.DataFrame:
        """
        Load the datos dataset from the given path.
        preferences are of level 1 or 2
        """
        return self._load_file(path, ['user','preference','score'])
    
    def load_ocupaciones(self, path: str = "data/ocupaciones.txt") -> pd.DataFrame:
        """
        Load the datos dataset from the given path.
        """
        return self._load_file(path, ['occupation','name'])
    
    def load_preferencias(self, path: str = "data/preferencias.txt") -> pd.DataFrame:
        """
        Load the datos dataset from the given path.
        """
        return self._load_file(path, ['preference','name','father'])
    
    def load_items(self, path: str = "data/items.txt") -> pd.DataFrame:
        """
        Load the datos dataset from the given path.
        """
        return self._load_file(path, ['item','name','views'])
    
    def load_clasificacion_items(self, path: str = "data/clasificacion_items.txt") -> pd.DataFrame:
        """
        Load the datos dataset from the given path.
        """
        return self._load_file(path, ['item','preference','score'])
    
    def _load_file(self, path: str , columns: list) -> pd.DataFrame:
        """
        Load the puntuaciones dataset from the given path.
        """
        with open(path, "r") as f:
            lines = f.readlines()

            # Procesar el archivo en bloques de 3 líneas
            data = [lines[i:i+len(columns)] for i in range(0, len(lines), len(columns))]

            # Convertir a un DataFrame
            df = pd.DataFrame(data, columns=columns)

            # Limpiar los saltos de línea
            df = df.map(lambda x: x.strip())

            # Mostrar el DataFrame
            return df

