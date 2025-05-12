from dash import register_page, html, dcc, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import json
import datetime

register_page(
    __name__,
    path='/preferences',
    title='Preferencias'
)

from src.data_loader import Data
user_info = Data().datos_personales

def create_preference_card(pref):
    return dbc.Card(
        [
            dbc.CardImg(src=pref["image"], className="pref-img"),
            dbc.CardBody(
                [
                    html.Div(pref["name"], className="text-center fw-semibold mb-2",
                             style={"fontSize":".85rem"}),
                    dcc.Slider(
                        id={"type": "pref-slider", "index": pref["id"]},
                        min=0, max=100, step=5, value=0,
                        marks={0:"0", 50:"50", 100:"100"},
                        tooltip={"placement":"bottom","always_visible":True},
                    ),
                ],
                className="p-2",
            )
        ],
        className="pref-card h-100"
    )


# Preference categories with image paths
preference_categories = [
    {"id": "1", "name": "Estilos y periodos", "image": "assets/pref1.png"},
    {"id": "2", "name": "Compras", "image": "assets/pref2.png"},
    {"id": "3", "name": "Museos", "image": "assets/pref3.png"},
    {"id": "4", "name": "Espacios Abiertos", "image": "assets/pref4.png"},
    {"id": "5", "name": "Arquitectura religiosa", "image": "assets/pref5.png"},
    {"id": "6", "name": "Arquitectura defensiva", "image": "assets/pref6.png"},
    {"id": "7", "name": "Arquitectura civil", "image": "assets/pref7.png"},
    {"id": "8", "name": "Gastronomia", "image": "assets/pref8.png"},
    {"id": "9", "name": "Deportes", "image": "assets/pref3.png"},
    {"id": "10", "name": "Monumentos", "image": "assets/pref10.png"},
    {"id": "11", "name": "Ocio", "image": "assets/pref11.png"},
    {"id": "12", "name": "Salud y SPA", "image": "assets/pref12.png"},
    {"id": "13", "name": "Eventos", "image": "assets/pref13.png"},
    {"id": "14", "name": "Niños", "image": "assets/pref14.png"},
    {"id": "15", "name": "Patrimonio de la Humanidad", "image": "assets/pref15.png"}
]

# Layout
layout = dbc.Container([
    html.H2("Ahora cuentanos acerca de tus preferencias de turismo:", className="my-4"),
    html.P("Asigna un valor del 0 al 100 a cada categoría según tu interés (mínimo 3)", className="mb-4"),
    
    # Grid container with fixed width
    html.Div(
        [
            # Row 1 (Preferences 1-5)
            dbc.Row([
                dbc.Col(create_preference_card(pref), 
                width=2.4, className="mb-4"
                ) for pref in preference_categories[0:5]
            ], className="g-3 mb-4"),
            
            # Row 2 (Preferences 6-10)
            dbc.Row([
                dbc.Col(create_preference_card(pref), 
                width=2.4, className="mb-4"
                ) for pref in preference_categories[5:10]
            ], className="g-3 mb-4"),
            
            # Row 3 (Preferences 11-15)
            dbc.Row([
                dbc.Col(create_preference_card(pref), 
                width=2.4, className="mb-4"
                ) for pref in preference_categories[10:15]
            ], className="g-3 mb-4")
        ],
        style={"maxWidth": "1200px", "margin": "0 auto","background-color": "#E0F8E0"}),
    
    # Submit button
    dbc.Button("Guardar Preferencias", 
               id="save-prefs", 
               color="success", 
               style={"background-color": "#5b93ad",  "border-color":     "#5b93ad"},
               className="mt-4 w-100",
               disabled=True),
    
    # Hidden storage
    dcc.Store(id="preferences-data"),
    
    # Confirmation message
    html.Div(id="pref-confirmation", className="mt-3")
],
fluid=True,
style={
        'backgroundColor': '#E0F8E0', 'position': 'fixed',
        'top': 0,        'left': 0,        'bottom': 0,        'right': 0,
        'overflow': 'auto'  # Allows scrolling if content exceeds viewport
    })

# Callback to enable submit button
@callback(
    Output("save-prefs", "disabled"),
    [Input({"type": "pref-slider", "index": ALL}, "value")]
)
def enable_submit_button(slider_values):
    selected_count = sum(1 for val in slider_values if val > 0)
    return selected_count < 3

