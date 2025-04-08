import dash
from dash import Dash, dcc, html, Output, Input, State, callback, ALL, register_page
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from src.data_loader import Data
import pandas as pd
import threading
import webbrowser
import json
import datetime

app = Dash(__name__, 
           external_stylesheets=[dbc.themes.BOOTSTRAP], 
           suppress_callback_exceptions=True,
           use_pages=True)

# Load data
user_info = Data().datos_personales

# Define layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Location(id='page_redirect', refresh=True),
    dcc.Store(id="user_id"),
    html.Div([
        dcc.Link('Inicio', href='/', className='btn btn-primary m-2'), 
        dcc.Link('Preferencias', href='/preferences', className='btn btn-secondary m-2'),
    ], className='text-center'),
    
    dash.page_container
])

# Importacion de las otras paginas al final de la app
from pages import home
from pages import preferences

############### home.py: cuando Sign up para agregar nuevo usuario ############### 
@callback(
    [Output("confirmation_message", "children"),
     Output("user_id", "data"),
     Output("page_redirect", "pathname")], 
    Input("submit_button", "n_clicks"),
    State("edad", "value"),
    State("sexo", "value"),
    State("ocupacion", "value"),
    State("hijos", "value"),
    State("edad_hijo_menor", "value"),
    State("edad_hijo_mayor", "value"),
    prevent_initial_call=True
)

def submit_user(n_clicks, edad, sexo, ocupacion, hijos, edad_hijo_menor, edad_hijo_mayor):
    global user_info

    # Validation
    if edad is None or sexo is None or ocupacion is None:
        return (dbc.Alert("Por favor, completa todos los campos obligatorios.", color="danger"),
                user_id, None)


    # Auto increment user_id
    user_id = user_info['user'].max() + 1 if not user_info.empty else 1
    nombre = f'User_{user_id}'
    
    # Hijos
    tiene_hijos = 1 if hijos and 1 in hijos else 0
    edad_hijo_menor = edad_hijo_menor if (tiene_hijos and edad_hijo_menor is not None) else 0
    edad_hijo_mayor = edad_hijo_mayor if (tiene_hijos and edad_hijo_mayor is not None) else 0

    # Nuevo usuario
    new_user = {
        'user': user_id,
        'name': nombre,
        'age': edad,
        'sex': sexo,
        'occupation': ocupacion,
        'children': tiene_hijos,
        'y_c_age': edad_hijo_menor,
        'o_c_age': edad_hijo_mayor
    }
    
    # Save to file (append mode)
    file_path = "data/usuarios_datos_personales.txt"
    with open(file_path, 'a') as f:
        f.write(f"{new_user['user']}\n")
        f.write(f"{new_user['name']}\n")
        f.write(f"{new_user['age']}\n")
        f.write(f"{new_user['sex']}\n")
        f.write(f"{new_user['occupation']}\n")
        f.write(f"{new_user['children']}\n")
        f.write(f"{new_user['y_c_age']}\n")
        f.write(f"{new_user['o_c_age']}\n")
    
    # Return success message
    return (
        dbc.Alert(f"✅ Usuario {nombre} registrado exitosamente. ¡Gracias!",  color="success"),
        user_id, 
        "/preferences"  # Redirect to preferences page
            )

############### preferences.py: Callback to save preferences ############### 
@callback(
    Output("pref-confirmation", "children"),
    Input("save-prefs", "n_clicks"),
    [State({"type": "pref-slider", "index": ALL}, "value"),
     State("user_id", "data")],     # <--- read from the same store
    prevent_initial_call=True
)
def save_preferences(n_clicks, slider_values, user_id):
    if not n_clicks:
        raise PreventUpdate

    if user_id is None:
        return dbc.Alert("❌ No se encontró el ID del usuario.", color="danger", className="mt-3")

    try:
        file_path = "data/usuarios_preferencias.txt"
        with open(file_path, "a") as f:
            for i, score in enumerate(slider_values):
                preference_id = str(i + 1)
                if score > 0:
                    f.write(f"{user_id}\n{preference_id}\n{score}\n")

        return dbc.Alert("✅ Preferencias guardadas exitosamente!", color="success", className="mt-3")

    except Exception as e:
        print(f"Error saving preferences: {str(e)}")
        return dbc.Alert(f"❌ Error al guardar: {str(e)}", color="danger", className="mt-3")


# Function to open browser automatically
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

# Run the Dash app in a separate thread
if __name__ == '__main__':
    threading.Timer(1, open_browser).start()  # Open the app in the browser
    app.run_server(debug=False, port=8050)