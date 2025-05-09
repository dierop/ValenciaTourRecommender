# pages/results.py -------------------------------------------------------------
from dash import html, dcc, callback, Input, Output, State, register_page
import dash
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from src.demographic_recommender import DemographicRecommender
from src.content_recommender     import ContentRecommender
# from src.collaborative_recommender import CollaborativeRecommender  # faltaria implementar
from src.utils_google import get_place_details                      

register_page(__name__, path="/results", name="Resultados")

from src.data_loader import Data
user_info = Data().datos_personales

# ------------------------------------------------------------------------------
# Layout

# ------------------------------------------------------------------------------
# Layout

layout = html.Div(                     # ① page wrapper
    className="results-page",
    children=[
        dbc.Card(                      # ② centred translucent card
            className="results-card",
            children=[
                dbc.Button("← Volver a Inicio",
                           href="/",
                           color="secondary",
                           className="btn-teal mb-4"),   # teal override

                html.H2("Resultados de la recomendación", className="mb-4"),
                dcc.Loading(html.Div(id="results-container"), type="circle"),
            ],
        )
    ]
)

# ------------------------------------------------------------------------------
# Callback

@callback(
    Output("results-container", "children"),
    Input("url", "pathname"),
    State("user", "data"),
    State("rec_settings", "data"),          # viene del Store de /recommender
    prevent_initial_call=False,             # run on first load
)

def build_results(_pathname, user_id, rec_settings):
    if user_id is None or rec_settings is None:
        return dbc.Alert("Faltan datos de usuario o configuración.", color="danger")

    n      = rec_settings.get("n_items", 10)
    algos  = rec_settings.get("algorithms", [])
    w_dict = rec_settings.get("weights", {})

    children = []

    # --- DEMOGRÁFICO -----------------------------------------------------------
    if "demografico" in algos:
        dr  = DemographicRecommender()
        rec = dr.recommend(user_id=user_id, n=n)   # [(id, name, score, group), ...]
        if rec:
            demographic_group = rec[0][3]
            children.append(html.H4(f"Recomendaciones demográficas (grupo {demographic_group})"))

            for pid, pname, score, _ in rec:
                children.extend(
                    _render_place_line(pid, pname, score)
                )

    # --- BASADO EN CONTENIDO ---------------------------------------------------
    if "contenido" in algos:
        cr  = ContentRecommender()
        rec = cr.recommend(user_id=user_id, n=n)
        if rec:
            children.append(html.H4("Recomendaciones basadas en contenido"))

            for pid, pname, score, _ in rec:
                children.extend(
                    _render_place_line(pid, pname, score)
                )

    # --- COLABORATIVO ----------------------------------------------
    #if "colaborativo" in algos:
        #cl  = ColabRecommender()
        #rec = cl.recommend(user_id=user_id, n=n)
        #if rec:
        #    children.append(html.H4("Recomendaciones basadas en algoritmo colaborativo"))

        #    for pid, pname, score, _ in rec:
        #        children.extend(
        #            _render_place_line(pid, pname, score)
        #        )

    if not children:
        children.append(
            dbc.Alert("No se generaron recomendaciones.", color="warning")
        )

    return children


# ------------------------------------------------------------------------------
# Fuction to search Google Maps for extra info

def _render_place_line(pid: str, pname: str, score: float):
    line = [html.Div(
            html.Strong(f"{pname}"),  # Bold text
            f" ({pid}) con certeza {round(score, 1)}",  # Regular text
            className="place-block")]

    gmaps = get_place_details(pname)
    if isinstance(gmaps, tuple) and len(gmaps) == 5:
        nombre, direccion, abierto, valoracion, n_val = gmaps
        line.append(
            html.Div(
                [
                    html.Small("Información adicional de Google Maps que le puede interesar:"),
                    html.Ul(
                        [
                            html.Li(f"{nombre}"),
                            html.Li(f"Dirección: {direccion}"),
                            html.Li(f"Abierto ahora: {abierto}"),
                            html.Li(f"Valoración: {valoracion} sobre {n_val} valoraciones"),
                        ],
                        className="ms-3",
                    ),
                ],
                className="text-muted",
            )
        )
    return line
