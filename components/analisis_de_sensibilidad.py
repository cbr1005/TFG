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
            dcc.Input(id='sens-spot', type='number', placeholder='Ingrese valor inicial', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Precio de ejercicio:', className="input-label"),
            dcc.Input(id='sens-strike', type='number', placeholder='Ingrese precio de ejercicio', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tasa de interés (%):', className="input-label"),
            dcc.Input(id='sens-rate', type='number', placeholder='Ingrese tasa de interés', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Volatilidad (%):', className="input-label"),
            dcc.Input(id='sens-volatility', type='number', placeholder='Ingrese volatilidad', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha actual:', className="input-label"),
            dcc.DatePickerSingle(id='sens-date-value', date=datetime.today().date(), className="date-picker"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha de vencimiento:', className="input-label"),
            dcc.DatePickerSingle(id='sens-date-expiration', date=None, className="date-picker"),
        ]),
        html.Div(id='sens-error-message', className="error-message-container"),
        html.Div(className="input-group", children=[
            html.Label('Tipo de opción:', className="input-label"),
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
     Output('sens-analysis-conclusion', 'children'),
     Output('sens-error-message', 'children')],
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
        missing_fields = []
        if spot is None:
            missing_fields.append("Precio al contado inicial")
        if strike is None:
            missing_fields.append("Precio de ejercicio")
        if rate is None:
            missing_fields.append("Tasa de interés")
        if volatility is None:
            missing_fields.append("Volatilidad")
        if date_value is None:
            missing_fields.append("Fecha actual")
        if date_expiration is None:
            missing_fields.append("Fecha de vencimiento")
        if not missing_fields:
            date_value = datetime.strptime(date_value, '%Y-%m-%d')
            date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d')

            if date_expiration <= date_value:
                error_message = html.Div([
                    html.H4("Error de Fecha:", style={'color': 'red'}),
                    html.P("La fecha de vencimiento debe ser posterior a la fecha actual.", style={'color': 'red'})
                ], style={'border': '2px solid red', 'padding': '10px', 'border-radius': '5px', 'margin-right': '20px'})
                return px.line(), html.Div(), error_message

            # Sensitivity analysis for option price vs. spot price
            spot_prices = np.linspace(spot * 0.5, spot * 1.5, 20)
            prices = [calcular_opcion_estandar_precio(s, strike, rate / 100, date_value, date_expiration, volatility / 100, option_type)[0][0] for s in spot_prices]
            deltas = [calcular_opcion_estandar_precio(s, strike, rate / 100, date_value, date_expiration, volatility / 100, option_type)[0][1] for s in spot_prices]

            df = pd.DataFrame({'Precio del Activo Subyacente': spot_prices, 'Valor de la Opción': prices, 'Delta': deltas})
            fig = px.line(df, x='Precio del Activo Subyacente', y='Valor de la Opción', title='Sensibilidad del Precio de la Opción respecto al Precio al Contado')

            conclusion = html.Div([
                html.H4("Conclusión del Análisis de Sensibilidad:"),
                html.P("Este análisis muestra cómo varía el precio de la opción respecto a cambios en el precio al contado del subyacente."),
                html.P(f"El rango de precios de la opción analizado va desde {prices[0]:.2f} hasta {prices[-1]:.2f}."),
                html.P("Comprender esta sensibilidad permite a los inversores anticipar cómo cambios en el mercado subyacente afectarán el valor de sus opciones, "
                       "lo cual es crucial para la gestión de riesgos y la toma de decisiones estratégicas.")
            ])

            return fig, conclusion, html.Div()  # No error, clear the error message
        else:
            error_message = html.Div([
                html.H4("Error de entrada:", style={'color': 'red'}),
                html.P("Los siguientes campos están vacíos y son requeridos: " + ", ".join(missing_fields), style={'color': 'red'})
            ], style={'border': '2px solid red', 'padding': '10px', 'border-radius': '5px', 'margin-right': '20px'})
            return px.line(), html.Div(), error_message

    return px.line(), html.Div(), html.Div()
