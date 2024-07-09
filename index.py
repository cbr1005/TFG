from dash import dcc, html, Input, Output
from dash_bootstrap_components import Container, Row, Col, Card, CardBody, Button
from app import app
from components.navbar import create_navbar
from components.sidebar import create_sidebar
from components.auth import login_layout
from components import simulaciones, simulacion_browniano, analisis_de_sensibilidad, comparacion_de_estrategias, comparacion_simulaciones


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='navbar-container', children=[create_navbar()]),
    html.Div(id='sidebar-container'),
    html.Div(id='page-content', className='mt-3')
])

@app.callback(
    [Output('page-content', 'children'),
     Output('sidebar-container', 'children')],
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/welcome':
        sidebar = create_sidebar()
        content = Container([
            Row([
                Col(html.H2("BIENVENIDOS", className="text-center mb-4"), width=12)
            ]),
            Row([
                Col(html.P(
                    "Bienvenidos a mi herramienta interactiva de análisis financiero. Aquí podrás realizar simulaciones de carteras de opciones, comparar estrategias de inversión, analizar la sensibilidad de las opciones frente a diferentes parámetros del mercado y explorar el impacto de la volatilidad. Utiliza los distintos módulos para obtener visualizaciones detalladas y tomar decisiones informadas.",
                    className="text-center mb-4"),
                    width=12),
            ]),
            Row([
                Col(Card([
                    CardBody([
                        html.H4("Simulación de Carteras", className="card-title text-center"),
                        html.P("Este código calcula precios de opciones financieras utilizando el modelo Black-Scholes y simulación de movimiento Browniano Geometrico, mostrando gráficas de la evolución del precio de la opción."),
                        Button("Explorar", href="/portfolio-simulation", className="stretched-link")
                    ])
                ], className="mb-3"), md=4),
                Col(Card([
                    CardBody([
                        html.H4("Simulación de Movimiento Browniano", className="card-title text-center"),
                        html.P("Calcula y compara precios de opciones Call y Put utilizando la simulación del movimiento Browniano Geometrico y visualiza la evolución del precio del activo subyacente."),
                        Button("Explorar", href="/montecarlo-simulation", className="stretched-link")
                    ])
                ], className="mb-3"), md=4),
                Col(Card([
                    CardBody([
                        html.H4("Análisis de Sensibilidad", className="card-title text-center"),
                        html.P("Analiza cómo varía el precio de una opción con cambios en el precio del activo subyacente, ayudando a evaluar diferentes escenarios de mercado."),
                        Button("Explorar", href="/sensitivity-analysis", className="stretched-link")
                    ])
                ], className="mb-3"), md=4),
            ]),
            Row([
                Col(Card([
                    CardBody([
                        html.H4("Comparación de Estrategias", className="card-title text-center"),
                        html.P("Compara diferentes estrategias de opciones basadas en condiciones de mercado como volatilidad y precios del activo subyacente."),
                        Button("Explorar", href="/strategy-comparison", className="stretched-link")
                    ])
                ], className="mb-3"), md=4),
                Col(Card([
                    CardBody([
                        html.H4("Comparación de Simulaciones", className="card-title text-center"),
                        html.P("Compara el impacto de diferentes niveles de volatilidad en el precio de las opciones y ofrece insights sobre cómo la volatilidad afecta al valor de las opciones."),
                        Button("Explorar", href="/option-simulation-comparison", className="stretched-link")
                    ])
                ], className="mb-3"), md=4),
            ])
        ], className="container",fluid=True)
        return content, sidebar
    elif pathname == '/login':
        return login_layout, None
    elif pathname == '/portfolio-simulation':
        return simulaciones.layout, create_sidebar()
    elif pathname == '/montecarlo-simulation':
        return simulacion_browniano.layout, create_sidebar()
    elif pathname == '/sensitivity-analysis':
        return analisis_de_sensibilidad.layout, create_sidebar()
    elif pathname == '/strategy-comparison':
        return comparacion_de_estrategias.layout, create_sidebar()
    elif pathname == '/option-simulation-comparison':
        return comparacion_simulaciones.layout, create_sidebar()
    else:
        return login_layout, None

if __name__ == '__main__':
    app.run_server(debug=True)
