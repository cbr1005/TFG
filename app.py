from dash import Dash
import dash_bootstrap_components as dbc

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# app.py
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdnjs.cloudflare.com/ajax/libs/boxicons/2.1.2/css/boxicons.min.css"
]

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
