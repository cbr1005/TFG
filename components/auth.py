from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from app import app


login_layout =(
    [
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H3("Iniciar Sesión", className="card-title"),
                        dbc.Input(id="username", placeholder="Usuario", type="text"),
                        dbc.Input(id="password", placeholder="Contraseña", type="password", style={'marginTop': 10}),
                        dbc.Button("Entrar", id="submit", color="primary", className="mt-3"),
                        html.Div(id="output-state", style={'marginTop': 30})  # Contenedor para el mensaje de error
                    ])
                ]),
                width=6
            ), justify="center",
            style={'marginTop': 50}
        )
    ]
)

@app.callback(
    Output('output-state', 'children'),
    Input('submit', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value'),
    prevent_initial_call=True,
)
def update_output(n_clicks, username, password):
    if n_clicks is None:
        return ""
    if username == "CarlosBarrio" and password == "TFG":
        return dcc.Location(pathname="/welcome", id="location-welcome")  # Redirige a la página de bienvenida
    else:
        # Muestra un mensaje de error si las credenciales son incorrectas
        return dbc.Alert("Usuario o contraseña incorrectos.", color="danger")
