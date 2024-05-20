from dash import html, dcc, callback, Input, Output, State
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime
import math
from components.funciones import calcular_opcion_estandar_precio

layout = html.Div([
    html.H1("Análisis de Escenarios", className="text-center title"),
    html.Div(className="input-container", children=[
        html.Div(className="input-group", children=[
            html.Label('Precio al contado:', className="input-label"),
            dcc.Input(id='scenario-spot', type='number', value=100, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Precio de ejercicio:', className="input-label"),
            dcc.Input(id='scenario-strike', type='number', value=100, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tasa de interes (%):', className="input-label"),
            dcc.Input(id='scenario-rate', type='number', value=2, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Volatilidad (%):', className="input-label"),
            dcc.Input(id='scenario-volatility', type='number', value=20, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha actual:', className="input-label"),
            dcc.DatePickerSingle(id='scenario-date-value', date='2024-05-01', className="date-picker"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha de vencimiento:', className="input-label"),
            dcc.DatePickerSingle(id='scenario-date-expiration', date='2024-11-01', className="date-picker"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tipo de opcion:', className="input-label"),
            dcc.Dropdown(
                id='scenario-option-type',
                options=[
                    {'label': 'Call', 'value': 'call'},
                    {'label': 'Put', 'value': 'put'}
                ],
                value='call',
                className="dropdown"
            ),
        ]),
        html.Button('Analizar Escenarios', id='scenario-button-analyze', n_clicks=0, className="calculate-button"),
    ]),
    dcc.Graph(id='scenario-analysis-graph', className="output-container"),
    html.Div(id='scenario-analysis-conclusion', className="output-container")
], className="container")

@callback(
    [Output('scenario-analysis-graph', 'figure'),
     Output('scenario-analysis-conclusion', 'children')],
    Input('scenario-button-analyze', 'n_clicks'),
    State('scenario-spot', 'value'),
    State('scenario-strike', 'value'),
    State('scenario-rate', 'value'),
    State('scenario-volatility', 'value'),
    State('scenario-date-value', 'date'),
    State('scenario-date-expiration', 'date'),
    State('scenario-option-type', 'value')
)
def analyze_scenarios(n_clicks, spot, strike, rate, volatility, date_value, date_expiration, option_type):
    if n_clicks > 0:
        date_value = datetime.strptime(date_value, '%Y-%m-%d')
        date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d')
        T = (date_expiration - date_value).days / 365

        scenarios = np.linspace(-0.2, 0.2, 5)  # Diferentes escenarios de cambios en la tasa de interés y la volatilidad
        results = []

        for s in scenarios:
            adjusted_rate = rate / 100 + s
            adjusted_volatility = volatility / 100 + s
            price = calcular_opcion_estandar_precio(spot, strike, adjusted_rate, date_value, date_expiration, adjusted_volatility, option_type)
            results.append({
                "Escenario": f"Rate: {adjusted_rate*100:.2f}%, Vol: {adjusted_volatility*100:.2f}%",
                "Precio Opción": price[0][0]
            })

        df = pd.DataFrame(results)
        fig = px.bar(df, x='Escenario', y='Precio Opción', title="Análisis de Escenarios")

        # Análisis de variación
        min_price = df['Precio Opción'].min()
        max_price = df['Precio Opción'].max()
        variation = max_price - min_price

        # Conclusión personalizada
        if variation > spot * 0.5:
            conclusion_text = "Los resultados muestran una alta sensibilidad del precio de la opción a cambios en la tasa de interés y la volatilidad. Esto indica un alto riesgo."
        elif variation > spot * 0.2:
            conclusion_text = "Los resultados muestran una sensibilidad moderada del precio de la opción a cambios en la tasa de interés y la volatilidad. Esto indica un riesgo moderado."
        else:
            conclusion_text = "Los resultados muestran una baja sensibilidad del precio de la opción a cambios en la tasa de interés y la volatilidad. Esto indica un bajo riesgo."

        conclusion = html.Div([
            html.H4("Conclusión del Análisis de Escenarios:"),
            html.P(conclusion_text),
            html.P(f"El precio de la opción varió entre {min_price:.2f} y {max_price:.2f} bajo los diferentes escenarios analizados. "
                   "Esto proporciona una visión de cómo los cambios en las condiciones del mercado pueden afectar el valor de la opción."),
            html.P("Utilizar esta herramienta permite evaluar el impacto de diversos escenarios de mercado en la valoración de opciones, ayudando a tomar decisiones "
                   "informadas para mitigar riesgos y maximizar beneficios.")
        ])

        return fig, conclusion
    
    return px.bar(), html.Div()
