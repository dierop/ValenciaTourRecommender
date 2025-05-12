# pages/groups_recommender.py 
# ---------------------------------------------------------------------------
from dash import html, dcc, callback, Input, Output, State, ALL, register_page
import dash
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

register_page(
    __name__,
    path="/groups_recommender",
    name="Recomendador grupal",
    title="Recomendaciones para grupos",
)

from src.data_loader import Data
user_info = Data().datos_personales

# --------------------------------------------------------------------- 
# layout

# --------------------------------------------------------------------- layout
layout = html.Div(                          # ① page wrapper
    className="recommender-page-groups",
    children=[
        dbc.Card(                           # ② translucent card
            className="recommender-card",
            children=[
                html.H2("Centro de recomendaciones para grupos", className="mb-4"),

                dbc.Row(
                    [
                        dbc.Col("Seleccione cuántas recomendaciones desea obtener:", width=8),
                        dbc.Col(
                            dcc.Input(
                                id="n-rec-input-groups",
                                type="number",
                                min=1, max=10, step=1,
                                placeholder="Hasta 10",
                                className="form-control",
                            ),
                            width=3,
                        ),
                    ],
                    className="mb-4 gx-2",
                ),

                html.H5("Seleccione qué sistema(s) desea usar o si los quiere combinar en uno híbrido con que pesos:"),
                dcc.Checklist(
                    id="algo-checklist-groups",
                    options=[
                        {"label": "Demográfico",            "value": "demografico"},
                        {"label": "Basado en contenido",    "value": "contenido"},
                        {"label": "Colaborativo (vecinos)", "value": "colaborativo"},
                        {"label": "Híbrido",    "value": "hibrido"},
                    ],
                    value=[],
                    inputStyle={"margin-right": "6px"},
                    className="mb-3",
                ),

                html.Div(id="weight-slider-container-groups"),

                dbc.Button(
                    "Obtener recomendaciones",
                    id="get-recs-btn-groups",
                    color="primary",              
                    className="btn-teal mt-2",    
                ),
                html.Div(id="recs-confirmation-groups", className="mt-3"),
            ],
        )
    ]
)

# ------------------------------------------------------------------- 
# Callbacks

@callback(
    Output("weight-slider-container-groups", "children"),
    Input("algo-checklist-groups", "value"),
)
def build_sliders(selected_algos):
    if not selected_algos:
        return dbc.Alert("Marca al menos un sistema recomendador.", color="info")

    # Only show sliders if "hibrido" is selected
    if "hibrido" not in selected_algos:
        return html.Div()

    # Define which algorithms should have sliders
    weighted_algos = ["demografico", "contenido", "colaborativo"]
    algo_labels = {
        "demografico": "Peso demográfico",
        "contenido": "Peso de contenido",
        "colaborativo": "Peso colaborativo"
    }

    sliders = []
    for algo in weighted_algos:
        sliders.append(
            dbc.Row(
                [
                    dbc.Col(algo_labels[algo], width=6),
                    dbc.Col(
                        dcc.Slider(
                            id={"type": "weight-slider", "index": algo},
                            min=0,
                            max=1,
                            step=0.1,
                            value=0,
                            marks={0.33333: "1/3", 0.66: "2/3", 1: "1"},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                        width=6,
                    ),
                ],
                className="mb-3"
            )
        )

    return sliders


