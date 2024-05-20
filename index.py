from dash import dcc, html, Input, Output, State
from app import app
from components.navbar import create_navbar
from components.sidebar import create_sidebar
from components.auth import login_layout
from components import simulacion_de_carteras, simulacion_montecarlo, analisis_de_escenarios, optimizacion_de_carteras, analisis_de_sensibilidad, comparacion_de_estrategias, comparacion_simulaciones, metodo_explicito, metodo_implicito, metodo_mesh, metodo_nicolson

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='navbar-container', children=[create_navbar()]),
    html.Div(id='sidebar-container'),
    html.Div(id='page-content')
])

@app.callback(
    [Output('page-content', 'children'),
     Output('sidebar-container', 'children')],
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/welcome':
        sidebar = create_sidebar()
        content = html.Div([
            html.H2("BIENVENIDOS", className="text-center", style={'marginTop': '100px'}),
            html.P("Aplicación web para la simulación de carteras", className="text-center"),
        ])
        return content, sidebar
    elif pathname == '/login':
        return login_layout, None
    elif pathname == '/portfolio-simulation':
        return simulacion_de_carteras.layout, create_sidebar()
    elif pathname == '/montecarlo-simulation':
        return simulacion_montecarlo.layout, create_sidebar()
    elif pathname == '/scenario-analysis':
        return analisis_de_escenarios.layout, create_sidebar()
    elif pathname == '/portfolio-optimization':
        return optimizacion_de_carteras.layout, create_sidebar()
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
    elif pathname == '/numeric-mesh':
        return metodo_mesh.layout, create_sidebar()
    elif pathname == '/numeric-nicolson':
        return metodo_nicolson.layout, create_sidebar()
    else:
        return login_layout, None

if __name__ == '__main__':
    app.run_server(debug=True)
