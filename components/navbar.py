# components/navbar.py
import dash_bootstrap_components as dbc
from dash import html

def create_navbar(with_dropdown=False):
    navbar_children = [
        dbc.Col(dbc.NavbarBrand("Cartera de Opciones", href="/welcome", className="text-center", style={'fontWeight': 'bold', 'fontSize': '2rem'}),
                className="flex-grow-1 text-center"),
    ]

    if with_dropdown:
        # Insert the sidebar toggle at the beginning of the children
        navbar_children.insert(0, dbc.Col(
            html.Button(
                # use the Bootstrap navbar-toggler classes to style
                html.Span(className="navbar-toggler-icon"),
                className="navbar-toggler",
                style={
                    "color": "rgba(0,0,0,.5)",
                    "borderColor": "rgba(0,0,0,.1)"
                },
                id="navbar-toggle",
            ),
            width="auto",
            className="me-auto",
        ))

    return dbc.Navbar(
        dbc.Row(navbar_children, align="center", className="w-100"),
        color="primary",
        dark=True,
        sticky="top",
    )


