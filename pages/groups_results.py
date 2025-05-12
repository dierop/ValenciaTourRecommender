# pages/results.py -------------------------------------------------------------
from dash import html, dcc, callback, Input, Output, State, register_page
import dash
import sys
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import importlib
from src.utils_google import get_place_details   

           # Register the page first
register_page(
    __name__,
    path="/groups_results",
    title="Resultados recomendación grupal"
)


# ------------------------------------------------------------------------------
# Layout

layout = html.Div(                     # ① page wrapper
    className="results-page-groups",
    children=[
        dbc.Card(                      # ② centred translucent card
            className="results-card",
            children=[
                dbc.Button("← Volver a Inicio",
                           href="/",
                           color="secondary",
                           className="btn-teal mb-4"),   # teal override

                html.H2("Resultados de la recomendación", className="mb-4"),
                dcc.Loading(html.Div(id="results-container-groups"), type="circle"),
            ],
        ),
        
    ]
)

# ------------------------------------------------------------------------------
# Callback

@callback(
    Output("results-container-groups", "children"),
    Input("url", "pathname"),
    State("group_ids", "data"),
    State("rec_groups_settings", "data"),          # viene del Store de /recommender
    prevent_initial_call=False,             # run on first load
)

def build_results(_pathname, group_ids, rec_groups_settings):
    # Force Python to re-execute those modules to find new users 
    if 'src.group_recommender' in sys.modules:
        importlib.reload(sys.modules['src.group_recommender'])
    from src.group_recommender import GroupRecommender
    

    n      = rec_groups_settings.get("n_items", 10)
    algos  = rec_groups_settings.get("algorithms", [])
    w_dict = rec_groups_settings.get("weights", {})

    children = []

    # --- GRUPOS -----------------------------------------------------------
    gr=GroupRecommender()
    rec = gr.group_recommend(
        users_id=group_ids,
        types=algos,
        checks=[w_dict['demografico'], w_dict['contenido'], w_dict['colaborativo']],
        n=n)

    if rec:
        children.append(html.H4("Recomendaciones para grupo: usando los algoritmos " + ", ".join(algos)))

        for pid, pname, score, _ in rec:
            children.extend(
                    _render_place_line(pid, pname, score))

    if not children:
        children.append(
            dbc.Alert("No se generaron recomendaciones. {w_dict}", color="warning")
        )

    return children


# ------------------------------------------------------------------------------
# Fuction to search Google Maps for extra info

def _render_place_line(pid: str, pname: str, score: float):
    line = [html.Div(
            [html.Strong(f"{pname}"),  # Bold text
            f" con proporción de preferencia en el grupo {round(score*100, 2)}"],  # Regular text
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
