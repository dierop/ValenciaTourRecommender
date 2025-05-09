# pages/recommender.py 
from dash import html, dcc, callback, Input, Output, State, ALL, register_page
import dash
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

register_page(
    __name__,
    path="/recommender",
    name="Recomendador",
    title="Recomendaciones"
)

# --------------------------------------------------------------------- 
# layout

layout = dbc.Container(
    [
        html.H2("Centro de recomendaciones", className="mb-4"),

        # Nº de ítems a recomendar
        dbc.Row(
            [
                dbc.Col("Seleccione cuántas recomendaciones desea obtener:", width=8),
                dbc.Col(
                    dcc.Input(
                        id="n-rec-input",
                        type="number",
                        min=1, max=10, step=1,
                        placeholder="Hasta 10",
                        className="form-control"
                    ),
                    width=3,
                ),
            ],
            className="mb-4 gx-2"
        ),

        # Checklist de sistemas recomendadores 
        html.H5("Seleccione qué sistema(s) desea usar:"),
        dcc.Checklist(
            id="algo-checklist",
            options=[
                {"label": "Demográfico",              "value": "demografico"},
                {"label": "Colaborativo (vecinos)",   "value": "colaborativo"},
                {"label": "Basado en contenido",      "value": "contenido"},
            ],
            value=[],
            inputStyle={"margin-right": "6px"},
            className="mb-3"
        ),

        # Sliders para los pesos aparecerán aquí ----------------------------------
        html.Div(id="weight-slider-container"),

        dbc.Button("Obtener recomendaciones", id="get-recs-btn", color="primary"),
        html.Div(id="recs-confirmation", className="mt-3"),
    ],
    className="pt-4"
)

# ------------------------------------------------------------------- 
# Callbacks

# 1) Mostrar / ocultar sliders según los checks 
@callback(
    Output("weight-slider-container", "children"),
    Input("algo-checklist", "value"),
)
def build_sliders(selected_algos):
    if not selected_algos:
        return dbc.Alert("Marca al menos un sistema recomendador.", color="info")

    sliders = []
    for algo in selected_algos:
        label = {
            "demografico":  "Peso demográfico",
            "colaborativo": "Peso colaborativo",
            "contenido":    "Peso de contenido",
        }[algo]

        sliders.append(
            dbc.Row(
                [
                    dbc.Col(label, width=6),
                    dbc.Col(
                        dcc.Slider(
                            id={"type": "weight-slider", "index": algo},
                            min=0,
                            max=100,
                            step=1,
                            value=33,                  
                            marks={33:"1/3",66:"2/3",100:"1"},
                            tooltip={"placement":"bottom","always_visible":False},
                        ),
                        width=6,
                    ),
                ],
                className="mb-3"
            )
        )
    return sliders


