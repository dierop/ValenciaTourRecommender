from dash import register_page, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import json

register_page(__name__, path="/preferences")

# Preference categories with image paths
preference_categories = [
    {"id": "pref1", "name": "Estilos y periodos", "image": "assets/pref1.jpg"},
    {"id": "pref2", "name": "Compras", "image": "assets/pref2.jpg"},
    {"id": "pref3", "name": "Museos", "image": "assets/pref3.jpg"},
    {"id": "pref4", "name": "Espacios Abiertos", "image": "assets/pref4.jpg"},
    {"id": "pref5", "name": "Arquitectura religiosa", "image": "assets/pref5.jpg"},
    {"id": "pref6", "name": "Arquitectura defensiva", "image": "assets/pref6.jpg"},
    {"id": "pref7", "name": "Arquitectura civil", "image": "assets/pref7.jpg"},
    {"id": "pref8", "name": "Gastronomia", "image": "assets/pref8.jpg"},
    {"id": "pref9", "name": "Deportes", "image": "assets/pref9.jpg"},
    {"id": "pref10", "name": "Monumentos", "image": "assets/pref10.jpg"},
    {"id": "pref11", "name": "Ocio", "image": "assets/pref11.jpg"},
    {"id": "pref12", "name": "Salud y SPA", "image": "assets/pref12.jpg"},
    {"id": "pref13", "name": "Eventos", "image": "assets/pref13.jpg"},
    {"id": "pref14", "name": "Niños", "image": "assets/pref14.jpg"},
    {"id": "pref15", "name": "Patrimonio de la Humanidad", "image": "assets/pref15.jpg"}
]

# Layout
layout = dbc.Container([
    html.H2("Ahora cuentanos acerca de tus preferencias de turismo:", className="my-4"),
    html.P("Cuales son las categorias que mas te interesan (clickealas al menos 3 en orden de interes)", className="mb-4"),
    
    # Grid of preference cards (3 rows x 5 columns)
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardImg(src=pref["image"], top=True),
                dbc.CardBody([
                    html.H5(pref["name"], className="card-title"),
                    dbc.Button("Seleccionar", 
                              id={"type": "pref-btn", "index": pref["id"]}, 
                              color="primary",
                              className="w-100")
                ])
            ], className="h-100"),
            width=4, className="mb-4"
        ) for pref in preference_categories[i:i+5]
    ], className="mb-4") for i in range(0, len(preference_categories), 5)],

    # Hidden div to store selected preferences
    dcc.Store(id="selected-preferences", data={"selected": [], "order": []}),
    
    # Submit button
    dbc.Button("Guardar Preferencias", id="save-prefs", color="success", className="mt-4"),
    
    # Confirmation message
    html.Div(id="pref-confirmation")
], fluid=True)

# Callback to handle preference selection
@callback(
    Output("selected-preferences", "data"),
    [Input({"type": "pref-btn", "index": ALL}, "n_clicks")],
    [State("selected-preferences", "data"),
     State({"type": "pref-btn", "index": ALL}, "id")],
    prevent_initial_call=True
)
def update_selected_preferences(clicks, current_data, buttons):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    # Get which button was clicked
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    button_id = json.loads(button_id)["index"]
    
    # Update selected preferences
    if button_id not in current_data["selected"]:
        current_data["selected"].append(button_id)
        current_data["order"].append(len(current_data["order"]) + 1)
    else:
        idx = current_data["selected"].index(button_id)
        current_data["selected"].pop(idx)
        current_data["order"].pop(idx)
    
    return current_data

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
        score = max(1 - (0.05 * (rank - 1)), 0.1)  # Minimum score of 0.1
        pref_scores[pref_id] = round(score, 2)
    
    # Create full preference vector (including unselected with 0)
    full_preferences = {}
    for pref in preference_categories:
        full_preferences[pref["id"]] = pref_scores.get(pref["id"], 0)
    
    # Save to user preferences (you might want to save to database instead)
    user_preferences = {
        user_id: [
            full_preferences["pref1"],  # Estilos y periodos
            full_preferences["pref2"],  # Compras
            # ... continue for all 15 categories
        ]
    }
    
    # Here you would typically save to a database
    print(f"Saved preferences for user {user_id}: {user_preferences}")
    
    return dbc.Alert("Preferencias guardadas exitosamente!", color="success")