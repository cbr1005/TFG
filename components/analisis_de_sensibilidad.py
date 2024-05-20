from dash import html, dcc, callback, Input, Output, State
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from components.funciones import calcular_opcion_estandar_precio

layout = html.Div([
    html.H1("Análisis de Sensibilidad", className="text-center title"),
    html.Div(className="input-container", children=[
        html.Div(className="input-group", children=[
            html.Label('Precio al contado inicial:', className="input-label"),
            dcc.Input(id='sens-spot', type='number', value=100, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Precio de ejercicio:', className="input-label"),
            dcc.Input(id='sens-strike', type='number', value=100, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tasa de interes (%):', className="input-label"),
            dcc.Input(id='sens-rate', type='number', value=2, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Volatilidad (%):', className="input-label"),
            dcc.Input(id='sens-volatility', type='number', value=20, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha actual:', className="input-label"),
            dcc.DatePickerSingle(id='sens-date-value', date='2024-05-01', className="date-picker"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha de vencimiento:', className="input-label"),
            dcc.DatePickerSingle(id='sens-date-expiration', date='2024-11-01', className="date-picker"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tipo de opcion:', className="input-label"),
            dcc.Dropdown(
                id='sens-option-type',
                options=[
                    {'label': 'Call', 'value': 'call'},
                    {'label': 'Put', 'value': 'put'}
                ],
                value='call',
                className="dropdown"
            ),
        ]),
        html.Button('Analizar Sensibilidad', id='sens-button-analyze', n_clicks=0, className="calculate-button"),
    ]),
    dcc.Graph(id='sens-analysis-graph', className="output-container"),
    html.Div(id='sens-analysis-conclusion', className="output-container")
], className="container")

@callback(
    [Output('sens-analysis-graph', 'figure'),
     Output('sens-analysis-conclusion', 'children')],
    Input('sens-button-analyze', 'n_clicks'),
    State('sens-spot', 'value'),
    State('sens-strike', 'value'),
    State('sens-rate', 'value'),
    State('sens-volatility', 'value'),
    State('sens-date-value', 'date'),
    State('sens-date-expiration', 'date'),
    State('sens-option-type', 'value')
)
def analyze_sensitivity(n_clicks, spot, strike, rate, volatility, date_value, date_expiration, option_type):
    if n_clicks > 0:
        date_value = datetime.strptime(date_value, '%Y-%m-%d')
        date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d')
        T = (date_expiration - date_value).days / 365

        # Sensibilidad respecto al precio al contado
        spot_prices = np.linspace(spot * 0.5, spot * 1.5, 20)
        prices = [calcular_opcion_estandar_precio(s, strike, rate / 100, date_value, date_expiration, volatility / 100, option_type)[0][0] for s in spot_prices]
        deltas = [calcular_opcion_estandar_precio(s, strike, rate / 100, date_value, date_expiration, volatility / 100, option_type)[0][1] for s in spot_prices]

        df = pd.DataFrame({'Spot Price': spot_prices, 'Option Price': prices, 'Delta': deltas})

        fig = px.line(df, x='Spot Price', y='Option Price', title='Sensibilidad del Precio de la Opción respecto al Precio al Contado')

        conclusion = html.Div([
            html.H4("Conclusión del Análisis de Sensibilidad:"),
            html.P("Este análisis muestra cómo varía el precio de la opción respecto a cambios en el precio al contado del subyacente."),
            html.P(f"El rango de precios de la opción analizado va desde {prices[0]:.2f} hasta {prices[-1]:.2f}."),
            html.P("Comprender esta sensibilidad permite a los inversores anticipar cómo cambios en el mercado subyacente afectarán el valor de sus opciones, "
                   "lo cual es crucial para la gestión de riesgos y la toma de decisiones estratégicas.")
        ])

        return fig, conclusion
    
    return px.line(), html.Div()
