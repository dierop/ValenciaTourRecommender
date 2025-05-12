# pages/detail_preferences.py
from dash import html, dcc, callback, Input, Output, State, ALL, register_page
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from src.data_loader import Data

register_page(
    __name__,
    path="/detail_preferences",
    name="Detalle de preferencias",
    title="Subpreferencias"
)

# ------------------------------------------------------------------------------
# Data
prefs_df = Data().preferences         
pref_categories = [ 
    {"id": "1", "name": "Estilos y periodos"},
    {"id": "2", "name": "Compras"},
    {"id": "3", "name": "Museos"},
    {"id": "4", "name": "Espacios Abiertos"},
    {"id": "5", "name": "Arquitectura religiosa"},
    {"id": "6", "name": "Arquitectura defensiva"},
    {"id": "7", "name": "Arquitectura civil"},
    {"id": "8", "name": "Gastronomia"},
    {"id": "9", "name": "Deportes"},
    {"id": "10", "name": "Monumentos"},
    {"id": "11", "name": "Ocio"}, 
    {"id": "12", "name": "Salud y SPA"},
    {"id": "13", "name": "Eventos"},
    {"id": "14", "name": "Niños"}, 
    {"id": "15", "name": "Patrimonio de la Humanidad"}
]

# ------------------------------------------------------------------------------
# Layout
# ----------------------------------------------------------------- Layout ----
layout = html.Div(                       # ① wrapper used by the CSS
    className="detail-page",
    children=[
        dbc.Card(                        # ② the soft card
            className="detail-card",
            children=[
                html.H3("¿Quieres agregar más detalle de tus preferencias?"),
                html.P("Marca la(s) categoría(s) que quieras detallar o deja todo vacío si no deseas añadir detalles:"),
                dcc.Checklist(
                    id="detail-cat-checklist",
                    className="detail-cat-checklist",
                    options=[{"label": c["name"], "value": c["id"]} for c in pref_categories],
                    value=[],
                    inputStyle={"margin-right": "6px"},
                ),

                html.Hr(),

                # Dynamic sub-preferences
                html.Div(id="subpref-container"),

                dbc.Button(
                    "Guardar detalle",
                    id="save-subprefs",
                    color="primary",             
                    className="btn-teal mt-4",    
                ),
                html.Div(id="subpref-confirmation", className="mt-3"),
            ],
        )
    ]
)

# -------------------------------------------------------------- Callbacks ----
@callback(
    Output("subpref-container", "children"),
    Input("detail-cat-checklist", "value"),
)
def build_subpref_inputs(selected_cat_ids):
    if not selected_cat_ids:
        return dbc.Alert("No has seleccionado ninguna categoría.", color="info")

    children = []
    for cat_id in selected_cat_ids:
        cat_name = next(c["name"] for c in pref_categories if c["id"] == cat_id)
        subprefs = prefs_df[prefs_df["father"].astype(int) == int(cat_id)]

        if subprefs.empty:
            continue

        children.append(html.H5(cat_name, className="mt-4"))
        for _, row in subprefs.iterrows():
            children.append(
                dbc.Row(
                    [
                        dbc.Col(f"{row['preference']}. {row['name']}", width=9),
                        dbc.Col(
                            dcc.Input(
                                id={"type": "subpref-score", "index": str(row["preference"])},
                                type="number", min=0, max=10, step=1, value=0,
                                className="form-control",
                            ),
                            width=3,
                        ),
                    ],
                    className="mb-2 subpref-row"      
                )
            )
    return children
