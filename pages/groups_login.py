# pages/groups_login.py
# ---------------------------------------------------------------------------
from dash import dcc, html, callback, Input, Output, State, register_page
import dash_bootstrap_components as dbc
import dash


# Register the page first
register_page(
    __name__,
    path="/groups_login",
    title="Recomendación grupal"
)

USER_OPTIONS = [{"label": str(i), "value": str(i)} for i in range(123, 181)]
MAX_INDIVIDUOS = 10

def _build_user_dropdown(idx: int) -> dbc.Row:
    return dbc.Row(
        [
            dbc.Col(html.Span(f"Usuario {idx+1}:"), width=3, className="pt-2"),
            dbc.Col(
                dcc.Dropdown(
                    id={"type": "user_id_dd", "index": idx},
                    options=USER_OPTIONS,
                    placeholder="Selecciona ID usuario",
                    clearable=False,
                ),
                width=9,
            ),
        ],
        className="mb-2",
    )

navbar = dbc.NavbarSimple(
    brand        = "Mi Guía Valencia",
    color        = "primary",
    dark         = True,
    className    = "mb-4",
    id="main-navbar",
)

# --- layout ---------------------------------------------------------------
layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H2("Registra tus compañeros para obtener la recomendación", className="text-center my-4")
            )
        ),

        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            # Input: cantidad de individuos -------------------
                            dbc.Row(
                                [
                                    dbc.Col(html.Label("Cantidad de individuos (1-10):"), width=6),
                                    dbc.Col(
                                        dbc.Input(
                                            id="cantidad_individuos",
                                            type="number",
                                            min=2,
                                            max=MAX_INDIVIDUOS,
                                            step=1,
                                            value=2,            
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-4",
                            ),

                            html.Div(id="user_id_inputs"),

                            dbc.Button(
                                "Obtener recomendación",
                                id="grupo_continuar_btn",
                                color="secondary",
                                className="btn-teal mb-4"),
                        ]
                    ),
                    className="login-card",
                ),
                width=8,
                className="offset-md-2",
            )
        ),
    html.Div(id="group_user_found_message", className="mt-3")],   
    className="login-page-groups",        
    fluid=True,
    style={
        "backgroundColor": "#E0F8E0",
        "minHeight": "100vh",
        "paddingBottom": "40px",
    },
)

# --- callbacks ------------------------------------------------------------
@callback(
    Output("user_id_inputs", "children"),
    Input("cantidad_individuos", "value"),
    prevent_initial_call=False,
)
def render_user_inputs(cantidad):
    if cantidad is None or cantidad < 1:
        return dbc.Alert("Indica un número de individuos (1-10).", color="warning")

    # clamp between 1 and MAX_INDIVIDUOS just in case
    cantidad = min(max(int(cantidad), 1), MAX_INDIVIDUOS)

    dropdowns = [_build_user_dropdown(i) for i in range(cantidad)]

    return html.Div(dropdowns)