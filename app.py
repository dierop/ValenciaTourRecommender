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
    dcc.Location(id='page_pref_redirect', refresh=True),
    dcc.Location(id='page_detail_redirect', refresh=True),
    dcc.Location(id='page_recs_redirect',    refresh=True),
    dcc.Store(id="user", storage_type="session"),
    dcc.Store(id="rec_settings", storage_type="session"),
    html.Div([
        dcc.Link('Inicio', href='/', className='btn btn-primary m-2'), 
        dcc.Link('Preferencias', href='/preferences', className='btn btn-secondary m-2'),
        dcc.Link('Subpreferencias', href='/detail_preferences', className='btn btn-success m-2'),
        dcc.Link('Recomendador',    href='/recommender',       className='btn btn-warning m-2'),
    ], className='text-center'),
    
    dash.page_container
])

# Importacion de las otras paginas al final de la app
from pages import home
from pages import preferences
from pages import detail_preferences  
from pages import recommender  

############### home.py: cuando Sign up para agregar nuevo usuario ############### 
@callback(
    [Output("confirmation_message", "children"),
     Output("user", "data", allow_duplicate=True),
     Output("page_pref_redirect", "pathname")], 
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

    # Auto increment user_id
    user_id = user_info['user'].max() + 1 if not user_info.empty else 1
    nombre = f'User_{user_id}'
    
    # Hijos
    tiene_hijos = 1 if hijos and 1 in hijos else 0
    edad_hijo_menor = edad_hijo_menor if (tiene_hijos and edad_hijo_menor is not None) else 0
    edad_hijo_mayor = edad_hijo_mayor if (tiene_hijos and edad_hijo_mayor is not None) else 0

    # Validation
    if edad is None or sexo is None or ocupacion is None:
        return (dbc.Alert("Por favor, completa todos los campos obligatorios.", color="danger"),
                user_id, None)

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
        user_id, # persist user_id in session
        "/preferences"  # Redirect to preferences page
            )

# 3) Login button con chequeo de si el usuario existe

db_users = Data().users

@callback(
    [Output("user_found_message", "children"),
     Output("user", "data", allow_duplicate=True),
     Output("page_recs_redirect", "pathname", allow_duplicate=True)],
    Input("login_button", "n_clicks"),         
    State("register_user", "value"),           
    prevent_initial_call=True
)

def go_to_recs_after_login(n_clicks, user):
    if not n_clicks:
        raise PreventUpdate
    try:
        uid = int(user)
    except (ValueError, TypeError):
        return dash.no_update                      

    if uid not in db_users["user"].values:
        return dash.no_update

    return (
        dbc.Alert(f"✅ Usuario {uid} encontrado en la base de datos",  color="success"),
        uid, # persist user_id in session
        "/recommender"  # Redirect to preferences page
            )

############### preferences.py: Callback to save preferences ############### 
@callback(
    [Output("pref-confirmation", "children"),
     Output("page_detail_redirect", "pathname")],
    Input("save-prefs", "n_clicks"),
    [State({"type": "pref-slider", "index": ALL}, "value"),
     State("user", "data")],    
    prevent_initial_call=True
)
def save_preferences(n_clicks, slider_values, user):
    if not n_clicks:
        raise PreventUpdate

    if user is None:
        return dbc.Alert("❌ No se encontró el ID del usuario.", color="danger", className="mt-3")

    try:
        file_path = "data/usuarios_preferencias.txt"
        with open(file_path, "a") as f:
            for i, score in enumerate(slider_values):
                preference_id = str(i + 1)
                if score > 0:
                    f.write(f"{user}\n{preference_id}\n{score}\n")

        return (dbc.Alert("✅ Preferencias guardadas exitosamente!", color="success", className="mt-3"),
                         "/detail_preferences"  # Redirect to subpreferences page
                         )

    except Exception as e:
        print(f"Error saving preferences: {str(e)}")
        return (dbc.Alert(f"❌ Error al guardar: {str(e)}", color="danger", className="mt-3"),
                dash.no_update)


############### detail_preferences.py: Callback to save subpreferences ############### 

@callback(
    [Output("subpref-confirmation", "children"),
    Output("page_recs_redirect", "pathname", allow_duplicate=True)],
    Input("save-subprefs", "n_clicks"),
    State({"type": "subpref-score", "index": ALL}, "value"),
    State({"type": "subpref-score", "index": ALL}, "id"),
    State("user", "data"),
    prevent_initial_call=True
)
def save_detail_prefs(n_clicks, scores, id_objects, user):
    if not n_clicks:
        raise PreventUpdate
    if user is None:
        return dbc.Alert("❌ No se encontró el ID del usuario.", color="danger")

    try:
        file_path = "data/usuarios_preferencias.txt"
        with open(file_path, "a") as f:
            for score, id_dict in zip(scores, id_objects):
                if not score or score == 0:
                    continue
                subpref_id = id_dict["index"]
                f.write(f"{user}\n{subpref_id}\n{score}\n")

        return (
            dbc.Alert("✅ Preferencias detalladas guardadas correctamente.", color="success"),
            "/recommender")
    except Exception as e:
        return (dbc.Alert(f"❌ Error al guardar: {str(e)}", color="danger"),
                dash.no_update)


############### detail_preferences.py: Callback to save config recomendaciones ############### 
# 2) Guardar config en Store  
@callback(
    [Output("rec_settings", "data"),
    Output("recs-confirmation", "children")],
    Input("get-recs-btn", "n_clicks"),
    State("n-rec-input", "value"),
    State("algo-checklist", "value"),
    State({"type": "weight-slider", "index": ALL}, "value"),
    State({"type": "weight-slider", "index": ALL}, "id"),
    prevent_initial_call=True,
)

def persist_rec_settings(n_clicks, n_items, algos, weights, slider_ids):
    if not n_clicks:
        raise PreventUpdate
    if n_items is None or n_items <= 0:
        return dash.no_update, dbc.Alert("Introduce un número de recomendaciones válido.", color="danger")

    # Build dict  algo -> weight (0-100)  keeping order of slider_ids
    weight_map = {id_["index"]: w for w, id_ in zip(weights, slider_ids)}

    data = {
        "n_items": n_items,
        "algorithms": algos,
        "weights": weight_map,
    }
    
    # Save to file (ver si vale la pena guardar en un archivo)
    with open("data/recommender_configs.txt", "w") as f:
        f.write(f"{data['n_items']}\n{data['algorithms']}\n{data['weights']}\n")

    return (data, dbc.Alert("✅ Parámetros guardados en sesión. Buscando la mejor recomendación...", color="success"))


# Function to open browser automatically
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

# Run the Dash app in a separate thread
if __name__ == '__main__':
    threading.Timer(1, open_browser).start()  # Open the app in the browser
    app.run_server(debug=True, port=8050)