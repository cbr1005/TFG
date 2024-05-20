from dash import html, dcc, callback, Input, Output, State
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from components.funciones import calcular_opcion_estandar_precio

layout = html.Div([
    html.H1("Comparación de Estrategias de Opciones", className="text-center title"),
    html.Div(className="input-container", children=[
        html.Div(className="input-group", children=[
            html.Label('Precio al contado:', className="input-label"),
            dcc.Input(id='comp-spot', type='number', value=100, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Precio de ejercicio:', className="input-label"),
            dcc.Input(id='comp-strike', type='number', value=100, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tasa de interes (%):', className="input-label"),
            dcc.Input(id='comp-rate', type='number', value=2, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Volatilidad (%):', className="input-label"),
            dcc.Input(id='comp-volatility', type='number', value=20, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha actual:', className="input-label"),
            dcc.DatePickerSingle(id='comp-date-value', date='2024-05-01', className="date-picker"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha de vencimiento:', className="input-label"),
            dcc.DatePickerSingle(id='comp-date-expiration', date='2024-11-01', className="date-picker"),
        ]),
        html.Button('Comparar Estrategias', id='comp-button-compare', n_clicks=0, className="calculate-button"),
    ]),
    dcc.Graph(id='comp-strategy-comparison-graph', className="output-container"),
    html.Div(id='comp-strategy-comparison-conclusion', className="output-container")
], className="container")

@callback(
    [Output('comp-strategy-comparison-graph', 'figure'),
     Output('comp-strategy-comparison-conclusion', 'children')],
    Input('comp-button-compare', 'n_clicks'),
    State('comp-spot', 'value'),
    State('comp-strike', 'value'),
    State('comp-rate', 'value'),
    State('comp-volatility', 'value'),
    State('comp-date-value', 'date'),
    State('comp-date-expiration', 'date')
)
def compare_strategies(n_clicks, spot, strike, rate, volatility, date_value, date_expiration):
    if n_clicks > 0:
        date_value = datetime.strptime(date_value, '%Y-%m-%d')
        date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d')
        T = (date_expiration - date_value).days / 365

        spot_prices = np.linspace(spot * 0.5, spot * 1.5, 100)

        strategies = {
            'Straddle': [],
            'Strangle': [],
            'Bull Spread': [],
            'Bear Spread': []
        }

        for s in spot_prices:
            call_price = calcular_opcion_estandar_precio(s, strike, rate / 100, date_value, date_expiration, volatility / 100, 'call')[0][0]
            put_price = calcular_opcion_estandar_precio(s, strike, rate / 100, date_value, date_expiration, volatility / 100, 'put')[0][0]

            straddle = call_price + put_price
            strangle = calcular_opcion_estandar_precio(s, strike * 0.9, rate / 100, date_value, date_expiration, volatility / 100, 'call')[0][0] + \
                       calcular_opcion_estandar_precio(s, strike * 1.1, rate / 100, date_value, date_expiration, volatility / 100, 'put')[0][0]
            bull_spread = calcular_opcion_estandar_precio(s, strike, rate / 100, date_value, date_expiration, volatility / 100, 'call')[0][0] - \
                          calcular_opcion_estandar_precio(s, strike * 1.1, rate / 100, date_value, date_expiration, volatility / 100, 'call')[0][0]
            bear_spread = calcular_opcion_estandar_precio(s, strike, rate / 100, date_value, date_expiration, volatility / 100, 'put')[0][0] - \
                          calcular_opcion_estandar_precio(s, strike * 0.9, rate / 100, date_value, date_expiration, volatility / 100, 'put')[0][0]

            strategies['Straddle'].append(straddle)
            strategies['Strangle'].append(strangle)
            strategies['Bull Spread'].append(bull_spread)
            strategies['Bear Spread'].append(bear_spread)

        df = pd.DataFrame({
            'Spot Price': spot_prices,
            'Straddle': strategies['Straddle'],
            'Strangle': strategies['Strangle'],
            'Bull Spread': strategies['Bull Spread'],
            'Bear Spread': strategies['Bear Spread']
        })

        fig = px.line(df, x='Spot Price', y=['Straddle', 'Strangle', 'Bull Spread', 'Bear Spread'], title='Comparación de Estrategias de Opciones')

        conclusion = html.Div([
            html.H4("Conclusión de la Comparación de Estrategias:"),
            html.P("Esta comparación muestra cómo diferentes estrategias de opciones se comportan en función de los cambios en el precio del subyacente."),
            html.Ul([
                html.Li("**Straddle**: Buena estrategia si se espera alta volatilidad, ya que combina una call y una put con el mismo strike."),
                html.Li("**Strangle**: Similar al straddle, pero utiliza strikes diferentes. Es menos costosa pero necesita mayor movimiento en el precio del subyacente para ser rentable."),
                html.Li("**Bull Spread**: Se utiliza cuando se espera un movimiento moderado al alza. Involucra la compra y venta de calls con diferentes strikes."),
                html.Li("**Bear Spread**: Se utiliza cuando se espera un movimiento moderado a la baja. Involucra la compra y venta de puts con diferentes strikes.")
            ]),
            html.P("Comparar estas estrategias ayuda a seleccionar la más adecuada según las expectativas del mercado y la tolerancia al riesgo.")
        ])

        return fig, conclusion
    
    return px.line(), html.Div()
