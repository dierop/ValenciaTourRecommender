from dash import register_page, html, dcc, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import json

register_page(__name__, path="/preferences")

# Preference categories with image paths
preference_categories = [
    {"id": "pref1", "name": "Estilos y periodos", "image": "assets/pref1.png"},
    {"id": "pref2", "name": "Compras", "image": "assets/pref2.png"},
    {"id": "pref3", "name": "Museos", "image": "assets/pref3.png"},
    {"id": "pref4", "name": "Espacios Abiertos", "image": "assets/pref3.png"},
    {"id": "pref5", "name": "Arquitectura religiosa", "image": "assets/pref3.png"},
    {"id": "pref6", "name": "Arquitectura defensiva", "image": "assets/pref3.png"},
    {"id": "pref7", "name": "Arquitectura civil", "image": "assets/pref3.png"},
    {"id": "pref8", "name": "Gastronomia", "image": "assets/pref3.png"},
    {"id": "pref9", "name": "Deportes", "image": "assets/pref3.png"},
    {"id": "pref10", "name": "Monumentos", "image": "assets/pref3.png"},
    {"id": "pref11", "name": "Ocio", "image": "assets/pref3.png"},
    {"id": "pref12", "name": "Salud y SPA", "image": "assets/pref3.png"},
    {"id": "pref13", "name": "Eventos", "image": "assets/pref3.png"},
    {"id": "pref14", "name": "Niños", "image": "assets/pref3.png"},
    {"id": "pref15", "name": "Patrimonio de la Humanidad", "image": "assets/pref3.png"}
]

# Layout
layout = dbc.Container([
    html.H2("Ahora cuentanos acerca de tus preferencias de turismo:", className="my-4"),
    html.P("Cuales son las categorias que mas te interesan (clickealas al menos 3 en orden de interes)", className="mb-4"),
    
    # Grid of preference cards (3 rows x 5 columns)
    *[dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardImg(
                            src=pref["image"],
                            top=True,
                            style={
                                "height": "120px",
                                "object-fit": "cover",
                                "cursor": "pointer"
                            }
                        ),
                        dbc.CardBody(
                            [
                                html.H6(
                                    pref["name"],
                                    className="card-title text-center",
                                    style={"font-size": "0.9rem"}
                                )
                            ],
                            className="p-2"
                        )
                    ],
                    id={"type": "pref-card", "index": pref["id"]},
                    style={
                        "height": "100%",
                        "border": "2px solid transparent",
                        "transition": "all 0.3s"
                    },
                    className="h-100"
                ),
                width=2.4, 
                className="mb-3"
            ) for pref in preference_categories[i:i+5]
        ],
        className="g-3"  # Adds consistent spacing between columns
    ) for i in range(0, len(preference_categories), 5)],
    
    # Hidden div to store selected preferences
    dcc.Store(id="selected-preferences", data={"selected": [], "order": []}),
    
    # Submit button
    dbc.Button("Guardar Preferencias", id="save-prefs", color="success", className="mt-4 w-100"),
    
    # Confirmation message
    html.Div(id="pref-confirmation")
],
fluid=True, style={"maxWidth": "1200px"})

@callback(
    [Output({"type": "pref-card", "index": ALL}, "style")],
    [Input({"type": "pref-card", "index": ALL}, "n_clicks")],
    [State("selected-preferences", "data"),
     State({"type": "pref-card", "index": ALL}, "style")],
    prevent_initial_call=True
)
def update_card_styles(clicks, selected_data, current_styles):
    ctx = callback_context
    if not ctx.triggered:
        return [current_styles]
    
    button_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])["index"]
    new_styles = current_styles.copy()
    
    for i, style in enumerate(new_styles):
        pref_id = preference_categories[i]["id"]
        if pref_id in selected_data["selected"]:
            style["border"] = "3px solid #0d6efd"  # Bootstrap primary blue
            style["box-shadow"] = "0 0 10px rgba(13, 110, 253, 0.5)"
        else:
            style["border"] = "2px solid transparent"
            style["box-shadow"] = "none"
    
    return [new_styles]

# Callback to save preferences
@callback(
    Output("pref-confirmation", "children"),
    Input("save-prefs", "n_clicks"),
    [State("selected-preferences", "data"),
     State("user_id", "data")],  # Assuming you pass user_id from previous page
    prevent_initial_call=True
)

def save_preferences(n_clicks, pref_data, user_id):
    if len(pref_data["selected"]) < 3:
        return dbc.Alert("Por favor selecciona al menos 3 preferencias", color="danger")
    
    # Calculate preference scores
    pref_scores = {}
    for i, (pref_id, rank) in enumerate(zip(pref_data["selected"], pref_data["order"])):
        # First selected gets 1, then subtract 0.05 for each position
        score = max(1 - (0.05 * (rank - 1)), 0)  
        pref_scores[pref_id] = round(score, 2)

    full_preferences = {}
    for pref in preference_categories:
        full_preferences[pref["id"]] = pref_scores.get(pref["id"], 0)
    
    # Save to user preferences
    user_preferences = {
        user_id: [
            full_preferences["pref1"],  # Estilos y periodos
            full_preferences["pref2"],  # Compras
            full_preferences["pref3"],  # Museos
            full_preferences["pref4"],  # Espacios Abiertos
            full_preferences["pref5"],  # Arquitectura religiosa
            full_preferences["pref6"],  # Arquitectura defensiva
            full_preferences["pref7"],  # Arquitectura civil
            full_preferences["pref8"],  # Gastronomia
            full_preferences["pref9"],  # Deportes
            full_preferences["pref10"], # Monumentos
            full_preferences["pref11"], # Ocio
            full_preferences["pref12"], # Salud y SPA
            full_preferences["pref13"], # Eventos
            full_preferences["pref14"], # Niños
            full_preferences["pref15"]  # Patrimonio de la Humanidad
        ]
    }
    
    # Save to JSON file
    with open("user_preferences.json", "a") as f:
        json.dump(user_preferences, f)
        f.write("\n")
    
    return dbc.Alert("Preferencias guardadas exitosamente!", color="success")