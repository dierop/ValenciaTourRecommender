import pandas as pd
import numpy as np
from kmodes.kprototypes import KPrototypes

def k_prototypes_clustering(df_merged, k):
    features = ['age', 'sex', 'children', 'y_c_age', 'o_c_age', 'name_y']
    df_clustering = df_merged[features].copy()

    numeric_cols = ['age', 'children', 'y_c_age', 'o_c_age']
    categorical_cols = ['sex', 'name_y']

    # Convierte columnas numéricas
    for col in numeric_cols:
        df_clustering[col] = pd.to_numeric(df_clustering[col], errors='coerce')

    # Limpieza completa de valores faltantes o infinitos
    df_clustering.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_clustering.dropna(subset=numeric_cols+categorical_cols, inplace=True)

    # Actualizar df_merged
    df_merged_clean = df_merged.loc[df_clustering.index].copy()

    # Convierte categóricas a string explícitamente
    for col in categorical_cols:
        df_clustering[col] = df_clustering[col].astype(str)

    # Verifica que todas las categóricas estén en el dataframe
    assert set(categorical_cols).issubset(set(df_clustering.columns)), \
        "Columnas categóricas faltantes en DataFrame."

    # Índices categóricos (robusto)
    categorical_indices = [df_clustering.columns.tolist().index(col) for col in categorical_cols]

    # K-Prototypes clustering
    kproto = KPrototypes(n_clusters=k, init='Cao', random_state=42, n_init=10)
    clusters = kproto.fit_predict(df_clustering, categorical=categorical_indices)

    df_clustering['cluster'] = clusters
    df_merged = df_merged.loc[df_clustering.index].copy()
    df_merged['cluster'] = clusters

    cluster_summary = {
        'size': df_clustering['cluster'].value_counts().to_dict(),
        'numeric_means': df_clustering.groupby('cluster')[numeric_cols].mean().to_dict(orient='index'),
        'categorical_distribution': {
            col: pd.crosstab(df_clustering['cluster'], df_clustering[col], normalize='index').to_dict()
            for col in categorical_cols
        }
    }

    return df_merged, cluster_summary


def mostrar_resumen_clusters(resumen_clusters):
    print("📌 **Resumen de Clústeres:**\n")
    
    sizes = resumen_clusters['size']
    numeric_means = resumen_clusters['numeric_means']
    cat_distributions = resumen_clusters['categorical_distribution']
    
    for cluster_id in sorted(sizes.keys()):
        print(f"\n{'='*40}")
        print(f"🔸 Clúster {cluster_id} - Usuarios: {sizes[cluster_id]}")
        print(f"{'='*40}\n")
        
        print("📊 Promedios numéricos:")
        for num_var, mean_value in numeric_means[cluster_id].items():
            print(f"  - {num_var}: {mean_value:.2f}")
        
        print("\n📌 Distribuciones categóricas:")
        for cat_var, distributions in cat_distributions.items():
            print(f"  → {cat_var}:")
            cluster_dist = distributions
            for cat_val, proportion in cluster_dist.items():
                val = proportion.get(cluster_id, 0)
                if val > 0:
                    print(f"      • {cat_val}: {val*100:.1f}%")
    print("\n" + "="*40 + "\n")