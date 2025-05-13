from dash import dcc, html, Output, Input, register_page, callback, State
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
import importlib
from src.data_loader import Data

refresh_modules = ["src.data_loader"]

# Register this page
register_page(
    __name__,
    path='/', 
    title='Inicio'
)

# Options for "Ocupación"
ocupacion_options = [
    {"label": "Fuerzas armadas", "value": "1"},
    {"label": "Dirección de las empresas y de las administraciones públicas", "value": "2"},
    {"label": "Técnicos y profesionales científicos e intelectuales", "value": "3"},
    {"label": "Técnicos y profesionales de apoyo", "value": "4"},
    {"label": "Empleados de tipo administrativo", "value": "5"},
    {"label": "Trabajadores de los servicios de restauración, personales, protección y vendedores de los comercios", "value": "6"},
    {"label": "Trabajadores cualificados en la agricultura y en la pesca", "value": "7"},
    {"label": "Artesanos y trabajadores cualificados de industrias manufactureras, construcción, y minería, excepto operadores de instalaciones y maquinaria", "value": "8"},
    {"label": "Operadores de instalaciones y maquinaria, y montadores", "value": "9"},
    {"label": "Trabajadores no cualificados", "value": "10"},
    {"label": "Inactivo o desocupado", "value": "11"}
]

# Login form individual
login_form = dbc.Card(
    dbc.CardBody(
        [
            dcc.Input(
                id="register_user",
                type="text",
                placeholder="Introduce tu ID de usuario",
                className="form-control mb-3",
            ),
            dbc.Button("Login",   id="login_button", color="primary",                      
                        style={"background-color": "#5b93ad",  "border-color":     "#5b93ad"}, className="me-2",),
            dbc.Button("Sign Up", id="signup_button", color="secondary"),
        ]
    ),
    style={
        "marginTop": "30px",          # separa ambas tarjetas
        "backgroundColor": "#f8f9fa",
        "padding": "20px",
        "borderRadius": "10px",
        "maxWidth": "800px"
    },
    className="login-card"
)

# Login form groups
group_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("¿Viajas en grupo y quieres obtener una recomendación para todos?", 
                    className="mb-3"),
            dbc.Button(
                "Recomendar en conjunto",
                id="grops_button",   
                color="primary",                      
                style={"background-color": "#5b93ad",  "border-color":     "#5b93ad"},
                className="w-100"
            ),
        ]
    ),
    className="login-card",
    style={
        "marginTop": "30px",          # separa ambas tarjetas
        "backgroundColor": "#f8f9fa",
        "padding": "20px",
        "borderRadius": "10px",
        "maxWidth": "800px"
    },
    id="group_card_container",
)

# App Layout
# ---------------------------------------------------------------------------
layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Hola, ¡bienvenid@ a tu guía turística de Valencia!",
                    className="text-center text-white my-4",
                    style={
                        "background-color": "#36a68a",
                        "padding": "10px",
                        "border-radius": "10px"
                    }
                ),
                width=12
            )
        ),

        # Tarjeta Login
        dbc.Row(
            dbc.Col(login_form, width=6, className="offset-md-3 text-center")
        ),

        # Tarjeta Recomendación en grupo  ▼▼
        dbc.Row(
            dbc.Col(group_card, width=6, className="offset-md-3 text-center")
        ),

        html.Div(id="signup_form", style={"marginTop": "30px"}),
        html.Div(id="confirmation_message", className="mt-3"),
        html.Div(id="user_found_message",   className="mt-3"),
    ],
    fluid=True,
    style={
        "backgroundColor": "#E0F8E0",
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "right": 0,
        "overflow": "auto",
    },
)

# ------------------------------------------------------------------- 
# Callbacks

# 1) Signup form
@callback(
    [Output("signup_form", "children"),
     Output("group_card_container",  "style")], 
    Input("signup_button", "n_clicks"),
    prevent_initial_call=True
)

def display_signup_form(n_clicks):
    return (dbc.Card(
        dbc.CardBody([
            html.H4("Registro de Usuario", className="text-center"),
            
            # Edad input
            dbc.Input(id="edad", type="number", placeholder="Edad", className="mb-3"),

            # Sexo RadioItems
            dbc.Row([
                dbc.Label("Sexo:", width=2),
                dbc.Col(
                    dbc.RadioItems(
                        options=[{"label": "Femenino", "value": "F"}, {"label": "Masculino", "value": "M"}],
                        value=None,
                        id="sexo",
                        inline=True
                    ),
                    width=10
                )
            ], className="mb-3"),

            # Ocupación Dropdown (fixed dropdown behavior)
            dbc.Row([
                dbc.Label("Ocupación:", width=2),
                dbc.Col(
                    dcc.Dropdown(
                        id="ocupacion",
                        options=ocupacion_options,
                        placeholder="Selecciona tu ocupación",
                        style={'width': '1000px', 'display': 'inline-block', 'margin-left': '10px', 
                               'margin-right': '10px'},
                    ),
                    width=10
                )
            ], className="mb-3"),

            # ¿Tienes hijos? Checklist
            dbc.Row([
                dbc.Label("¿Tienes hijos?", width=2),
                dbc.Col(
                    dbc.Checklist(
                        options=[{"label": "Sí", "value": 1}],
                        value=[],
                        id="hijos",
                        inline=True
                    ),
                    width=10
                )
            ], className="mb-3"),

            # Edad hijos (conditional inputs)
            html.Div(
                [
                    dbc.Input(id="edad_hijo_menor", type="number",
                              placeholder="Edad hijo menor",
                              className="mb-2", style={"display": "none"}),
                    dbc.Input(id="edad_hijo_mayor", type="number",
                              placeholder="Edad hijo mayor",
                              className="mb-2", style={"display": "none"})
                ],
                id="hijos_edades"),

            # Submit Button
            dbc.Button("Enviar", id="submit_button", color="primary",style={"background-color": "#5b93ad",  "border-color":     "#5b93ad"}, className="w-100 mt-4")
        ]),
        style={"maxWidth": "1300px", "margin": "auto", "marginTop": "20px", "backgroundColor": "#f8f9fa", "padding": "20px", "borderRadius": "10px"}
    ), {"display": "none"})


# 2) Show/hide edad_hijo_menor and edad_hijo_mayor based on "¿Tienes hijos?"
@callback(
    [
        Output("hijos_edades", "children"),
        Output("hijos_edades", "style")
    ],
    Input("hijos", "value")
)
def toggle_hijos_fields(hijos):
    if hijos and 1 in hijos:
        return (
            html.Div([
                dbc.Input(id="edad_hijo_menor", type="number", placeholder="Edad hijo menor", className="mb-2"),
                dbc.Input(id="edad_hijo_mayor", type="number", placeholder="Edad hijo mayor", className="mb-2")
            ]),
            {"display": "block"}
        )
    else:
        return (None, {"display": "none"})
    

