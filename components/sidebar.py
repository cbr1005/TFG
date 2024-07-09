from dash import html
import dash_bootstrap_components as dbc

def create_sidebar():
    return html.Div(
        [
            dbc.Nav(
                [
                    dbc.NavLink(
                        [html.I(className="bx bx-home"), html.Span("Inicio", className="d-none d-md-inline")],
                        href="/welcome",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [html.I(className="bx bx-play-circle"), html.Span("Simulación de Carteras", className="d-none d-md-inline")],
                        href="/portfolio-simulation",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [html.I(className="bx bx-line-chart"), html.Span("Simulación Movimiento Browniano", className="d-none d-md-inline")],
                        href="/montecarlo-simulation",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [html.I(className="bx bx-move"), html.Span("Análisis de Sensibilidad", className="d-none d-md-inline")],
                        href="/sensitivity-analysis",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [html.I(className="bx bx-intersect"), html.Span("Comparación de Estrategias", className="d-none d-md-inline")],
                        href="/strategy-comparison",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [html.I(className="bx bx-layer"), html.Span("Comparación de Simulaciones", className="d-none d-md-inline")],
                        href="/option-simulation-comparison",
                        active="exact",
                    ),
                ],
                vertical=True,
                pills=True,
                className="sidebar",
            ),
        ]
    )
