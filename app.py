import dash
from dash import Dash, dcc, html, Output, Input, State, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
import threading
import webbrowser
import json
import datetime

# Initialize Dash app with suppress_callback_exceptions
app = Dash(__name__, 
           external_stylesheets=[dbc.themes.BOOTSTRAP], 
           suppress_callback_exceptions=True,
           use_pages=True)

# Initialize DataFrame with example users
user_info = pd.DataFrame({
    'user_id': range(1, 11),
    'Nombre': [f'User_{i}' for i in range(1, 11)],
    'Edad': [25 + i for i in range(10)],
    'Sexo': ['F' if i % 2 == 0 else 'M' for i in range(10)],
    'Ocupación': [str((i % 11) + 1) for i in range(10)],
    'Hijos': [1 if i % 3 == 0 else 0 for i in range(10)],
    'Edad_hijo_menor': [5 if i % 3 == 0 else 0 for i in range(10)],
    'Edad_hijo_mayor': [8 if i % 3 == 0 else 0 for i in range(10)]
})

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    
    # Navigation
    html.Div([
        dcc.Link('Inicio', href='/home', className='btn btn-primary m-2'),
        dcc.Link('Preferencias', href='/preferences', className='btn btn-secondary m-2'),
    ], className='text-center'),
    
    dash.page_container
])

############### home.py: cuando Sign up para agregar nuevo usuario ############### 
@callback(
    [Output("confirmation_message", "children"),
     Output("url", "pathname")], 
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
        return dbc.Alert("Por favor, completa todos los campos obligatorios.", color="danger")

    # Auto increment user_id
    user_id = user_info['user_id'].max() + 1 if not user_info.empty else 1
    nombre = f'User_{user_id}'
    
    # Hijos
    tiene_hijos = 1 if hijos and 1 in hijos else 0
    edad_hijo_menor = edad_hijo_menor if tiene_hijos else 0
    edad_hijo_mayor = edad_hijo_mayor if tiene_hijos else 0

    # Nuevo usuario
    new_user = {
        'user_id': user_id,
        'Nombre': nombre,
        'Edad': edad,
        'Sexo': sexo,
        'Ocupación': ocupacion,
        'Hijos': tiene_hijos,
        'Edad_hijo_menor': edad_hijo_menor,
        'Edad_hijo_mayor': edad_hijo_mayor
    }
    
    # Add new user to the DataFrame
    user_info = pd.concat([user_info, pd.DataFrame([new_user])], ignore_index=True)
    
    
    # Return success message
    return (
        dbc.Alert(f"✅ Usuario {nombre} registrado exitosamente. ¡Gracias!",  color="success"),
        "/preferences"  # Redirect to preferences page
            )

############### preferences.py: Callback to save preferences ############### 
@callback(
    [Output("pref-confirmation", "children"),
     Output("preferences-data", "data")],
    Input("save-prefs", "n_clicks"),
    [State({"type": "pref-slider", "index": ALL}, "value"),
     State("user_id", "data")],
    prevent_initial_call=True
)
def save_preferences(n_clicks, slider_values, user_id):
    if not n_clicks:
        raise PreventUpdate
    
    # Create ordered list of all 15 preferences
    ordered_preferences = [val for val in slider_values]
    
    user_preferences = {
        "user_id": user_id,
        "preferences": ordered_preferences,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    try:
        # Save to JSON file
        with open("user_preferences.json", "a") as f:
            json.dump(user_preferences, f, ensure_ascii=False)
            f.write("\n")
        
        # Print to console for debugging
        print(f"Saved preferences: {user_preferences}")
        
        return (
            dbc.Alert("✅ Preferencias guardadas exitosamente!", color="success", className="mt-3"),
            user_preferences
        )
    except Exception as e:
        print(f"Error saving preferences: {str(e)}")
        return (
            dbc.Alert(f"❌ Error al guardar: {str(e)}", color="danger", className="mt-3"),
            None
        )

# Importacion de las otras paginas al final de la app
from pages import home
from pages import preferences

# Function to open browser automatically
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

# Run the Dash app in a separate thread
if __name__ == '__main__':
    threading.Timer(1, open_browser).start()  # Open the app in the browser
    app.run_server(debug=False, port=8050)