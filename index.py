from dash import dcc, html, Input, Output, State
from dash_bootstrap_components import Container, Row, Col, Card, CardBody, Button
from app import app
from components.navbar import create_navbar
from components.sidebar import create_sidebar
from components.auth import login_layout
from components import simulaciones, simulacion_montecarlo, analisis_de_sensibilidad, comparacion_de_estrategias, comparacion_simulaciones, metodo_explicito, metodo_implicito


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
                        html.P("Este código calcula precios de opciones financieras utilizando el modelo Black-Scholes y simulación de Monte Carlo, mostrando gráficas de la evolución del precio de la opción."),
                        Button("Explorar", href="/portfolio-simulation", className="stretched-link")
                    ])
                ], className="mb-3"), md=4),
                Col(Card([
                    CardBody([
                        html.H4("Simulación de Monte Carlo", className="card-title text-center"),
                        html.P("Calcula y compara precios de opciones Call y Put utilizando la simulación de Monte Carlo y visualiza la evolución del precio del activo subyacente."),
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
                Col(Card([
                    CardBody([
                        html.H4("Métodos Numéricos", className="card-title text-center"),
                        html.P("Explora métodos numéricos como diferencias finitas explícitas e implícitas para calcular precios de opciones financieras.")
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
        return simulacion_montecarlo.layout, create_sidebar()
    elif pathname == '/sensitivity-analysis':
        return analisis_de_sensibilidad.layout, create_sidebar()
    elif pathname == '/strategy-comparison':
        return comparacion_de_estrategias.layout, create_sidebar()
    elif pathname == '/option-simulation-comparison':
        return comparacion_simulaciones.layout, create_sidebar()
    elif pathname == '/numeric-explicit':
        return metodo_explicito.layout, create_sidebar()
    elif pathname == '/numeric-implicit':
        return metodo_implicito.layout, create_sidebar()
    else:
        return login_layout, None

if __name__ == '__main__':
    app.run_server(debug=True)


