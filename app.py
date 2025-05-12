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
server = app.server

# Load data
user_info = Data().datos_personales

# Define layout
app.layout = html.Div([

    dcc.Location(id='url', refresh=False),
    dcc.Location(id='page_pref_redirect', refresh=True),
    dcc.Location(id='page_results_redirect', refresh=True),
    dcc.Location(id='page_detail_redirect', refresh=True),
    dcc.Location(id='page_recs_redirect',    refresh=True),

    dcc.Location(id='page_group_redirect', refresh=True),
    dcc.Location(id='page_groups_recs_redirect',    refresh=True),
    dcc.Location(id='page_groups_results_redirect',    refresh=True),

    dcc.Store(id="user", storage_type="session"),
    dcc.Store(id="rec_settings", storage_type="session"),
    
    dcc.Store(id="group_ids", storage_type="session"), 
    dcc.Store(id="rec_groups_settings", storage_type="session"),

    html.Div([
        dcc.Link('Inicio', href='/', className='btn btn-primary m-2'), 
        dcc.Link('Preferencias', href='/preferences', className='btn btn-secondary m-2'),
        dcc.Link('Subpreferencias', href='/detail_preferences', className='btn btn-success m-2'),
        dcc.Link('Algoritmos',    href='/recommender',       className='btn btn-warning m-2'),
        dcc.Link('Recomendacion',    href='/results',       className='btn btn-warning m-2'),
        dcc.Link('Inicio Grupos',    href='/groups_login',       className='btn btn-warning m-2'),
        dcc.Link('Algoritmos Grupos',    href='/groups_recommender',       className='btn btn-warning m-2'),
        dcc.Link('Recomendacion Grupos',    href='/groups_results',       className='btn btn-warning m-2'),
    ], 
    id="top-nav", className='text-center'),
    
    dash.page_container
])

# Importacion de las otras paginas al final de la app
from pages import home
from pages import preferences
from pages import detail_preferences  
from pages import recommender  

# app.py  Callback para ocultar el navbar

@callback(
    Output("top-nav", "style"),
    Input("url", "pathname"),
)
def hide_nav_on_detail(pathname):
    hidden_pages = {"/detail_preferences", "/recommender", "/results", "/groups_login", "/groups_recommender", "/groups_results"} 
    if pathname in hidden_pages:
        return {"display": "none"}
    return {}

##############################  home.py  ############################## 
 
#### 1) Sign up para agregar nuevo usuario (-> preferences.py)
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

    if edad is None or sexo is None or ocupacion is None:
        return (dbc.Alert("Por favor, completa todos los campos obligatorios.", color="danger"),
                user_id, None)

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
    
    return (
        dbc.Alert(f"✅ Usuario {nombre} registrado exitosamente. ¡Gracias!",  color="success"),
        user_id, # persist user_id in session
        "/preferences" 
            )

#### 2) Login button con chequeo de si el usuario existe (-> recommender.py)

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
        return (
            dbc.Alert("❌ Número de usuario no válido, introduzca un ID válido o regístrese.", color="danger"),
            dash.no_update,          # no tocar el Store "user"
            dash.no_update           # no redirigir
        )

    if uid not in db_users["user"].values:
        return (
            dbc.Alert("❌ Usuario no encontrado, introduzca un ID válido o regístrese.", color="danger"),
            dash.no_update,
            dash.no_update
        )

    return (
        dbc.Alert(f"✅ Usuario {uid} encontrado en la base de datos",  color="success"),
        uid, # persist user_id in session
        "/recommender"  
            )

#### 3) Redireccion a recomendaciones en grupo (-> groups_login.py)
@callback(
    Output("page_group_redirect", "pathname"),
    Input("grops_button", "n_clicks"),  
    prevent_initial_call=True,
)
def redirect_to_group_login(n_clicks):
    if not n_clicks:            
        raise PreventUpdate
    return "/groups_login"      



############### preferences.py: Callback to save preferences (-> detail_preferences.py) ############### 
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
                         "/detail_preferences"  
                         )

    except Exception as e:
        print(f"Error saving preferences: {str(e)}")
        return (dbc.Alert(f"❌ Error al guardar: {str(e)}", color="danger", className="mt-3"),
                dash.no_update)


############### detail_preferences.py: Callback to save subpreferences (-> recommender.py)############### 

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


############### recommender.py: Callback to save config recomendaciones (-> results.py) ############### 
@callback(
    [Output("rec_settings", "data"),
     Output("recs-confirmation", "children"),
     Output("page_results_redirect", "pathname")],
    Input("get-recs-btn", "n_clicks"),
    State("n-rec-input", "value"),
    State("algo-checklist", "value"),
    State({"type": "weight-slider", "index": ALL}, "value"),
    prevent_initial_call=True,
)
def persist_rec_settings(n_clicks, n_items, algos, weights):
    if not n_clicks:
        raise PreventUpdate
    if n_items is None or n_items <= 0:
        return dash.no_update, dbc.Alert("Introduce un número de recomendaciones válido.", color="danger"), dash.no_update

    dic_weights = {id: w for w, id in zip(weights, ["demografico", "contenido", "colaborativo"])}
    data = {
        "n_items": n_items,
        "algorithms": algos,
        "weights": dic_weights}

    return (
        data,
        dbc.Alert("✅ Parámetros guardados en sesión. Buscando la mejor recomendación...", color="success"),
        "/results"
    )


################################################# GROUPS ####################################################

############### groups_login.py: Callback to save preferences (-> groups_recommender.py)############### 
@callback([Output("group_user_found_message", "children"),
     Output("group_ids", "data"),
     Output("page_groups_recs_redirect", "pathname", allow_duplicate=True)],
    Input("grupo_continuar_btn", "n_clicks"),                    
    State({"type": "user_id_dd", "index": ALL}, "value"),        
    prevent_initial_call=True,
)
def save_group_ids(n_clicks, selected_ids):
    if not n_clicks:                    
        raise PreventUpdate

    cleaned = [int(uid) for uid in selected_ids if uid is not None]
    cleaned_text = [str(uid) for uid in selected_ids if uid is not None]
    cleaned = list(dict.fromkeys(cleaned))
    text = ", ".join(cleaned_text)         

    return (
        dbc.Alert(f"✅ Grupo de {text} individuos registrado",  color="success"),
        cleaned, 
        "/groups_recommender"  
            )       

############### recommender.py: Callback to save config recomendaciones (-> groups_results.py) ############### 
@callback(
    [Output("rec_groups_settings", "data"),
     Output("recs-confirmation-groups", "children"),
     Output("page_groups_results_redirect", "pathname")],
    Input("get-recs-btn-groups", "n_clicks"),
    State("n-rec-input-groups", "value"),
    State("algo-checklist-groups", "value"),
    State({"type": "weight-slider", "index": ALL}, "value"),
    prevent_initial_call=True,
)
def persist_rec_settings(n_clicks, n_items, algos, weights):
    if not n_clicks:
        raise PreventUpdate
    if n_items is None or n_items <= 0:
        return dash.no_update, dbc.Alert("Introduce un número de recomendaciones válido.", color="danger"), dash.no_update

    dic_weights = {id: w for w, id in zip(weights, ["demografico", "contenido", "colaborativo"])}
    data = {
        "n_items": n_items,
        "algorithms": algos,
        "weights": dic_weights}

    return (
        data,
        dbc.Alert("✅ Parámetros guardados en sesión. Buscando la mejor recomendación...", color="success"),
        "/groups_results"
    )




############################ Launch app ############################
#  Function to open browser automatically
#def open_browser():
#    webbrowser.open_new("http://127.0.0.1:8050/")

# Run the Dash app in a separate thread
if __name__ == '__main__':
    #threading.Timer(1, open_browser).start()  
    app.run_server(debug=True, host="0.0.0.0", port=8050) 