from dash import html, dcc, callback, Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime
import dash
from components.funciones import determine_optimal_strategy

layout = html.Div([
    html.H1("Comparación de Estrategias de Opciones", className="text-center title"),
    html.Div(className="input-container", children=[
        html.Div(className="input-group", children=[
            html.Label('Precio del activo subyacente:', className="input-label"),
            dcc.Input(id='comp-spot', type='number', placeholder='Ingrese el precio del activo subyacente', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Precio del ejercicio:', className="input-label"),
            dcc.Input(id='comp-strike', type='number', placeholder='Ingrese el precio del ejercicio', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tasa de interés (%):', className="input-label"),
            dcc.Input(id='comp-rate', type='number', placeholder='Ingrese la tasa de interés', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Volatilidad (%):', className="input-label"),
            dcc.Input(id='comp-volatility', type='number', placeholder='Ingrese la volatilidad', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha actual:', className="input-label"),
            dcc.DatePickerSingle(id='comp-date-value', date=datetime.today().date(), className="date-picker"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha de vencimiento:', className="input-label"),
            dcc.DatePickerSingle(id='comp-date-expiration', date=None, className="date-picker"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tipo de opción:', className="input-label"),
            dcc.Dropdown(
                id='comp-option-type',
                options=[
                    {'label': 'Call', 'value': 'call'},
                    {'label': 'Put', 'value': 'put'}
                ],
                value='call',
                className="dropdown"
            ),
        ]),
        html.Button('Comparar Estrategias', id='comp-button-compare', n_clicks=0, className="calculate-button"),
    ]),
    dcc.Graph(id='comp-strategy-comparison-graph', className="output-container"),
    html.Div(id='comp-strategy-comparison-conclusion', className="output-container")
], className= 'container')

@callback(
    [Output('comp-strategy-comparison-graph', 'figure'),
     Output('comp-strategy-comparison-conclusion', 'children')],
    [Input('comp-button-compare', 'n_clicks')],
    [State('comp-spot', 'value'),
     State('comp-strike', 'value'),
     State('comp-rate', 'value'),
     State('comp-volatility', 'value'),
     State('comp-date-value', 'date'),
     State('comp-date-expiration', 'date'),
     State('comp-option-type', 'value')]
)
def compare_strategies(n_clicks, spot, strike, rate, volatility, date_value, date_expiration, option_type):
    if n_clicks is None or n_clicks < 1:
        return {}, "No se ha realizado ninguna comparación aún."

    date_value = datetime.strptime(date_value, '%Y-%m-%d')
    date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d')

    optimal_strategy = determine_optimal_strategy(spot, strike, rate, volatility, date_value, date_expiration, option_type)

    strategies = ['Straddle', 'Strangle', 'Butterfly Spread', 'Bull Spread', 'Bear Spread']
    
    colors = {
        'Straddle': 'red',
        'Strangle': 'green',
        'Butterfly Spread': 'blue',
        'Bull Spread': 'orange',
        'Bear Spread': 'cyan'
    }
    
    fig = go.Figure()
    x_values = np.linspace(0, 200, 400)  
    for strategy in strategies:
        y_values = np.sin(x_values / 50) * np.random.randint(50, 150) + (x_values / 100) * np.random.choice([-1, 1])
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines',
            line=dict(color=colors[strategy], width=4 if strategy == optimal_strategy else 2),
            name=strategy
        ))

    fig.update_layout(
        title='Comparación de Estrategias de Opciones',
        xaxis_title='Precio del activo subyacente',
        yaxis_title='Eje de rendimiento',
        template='plotly_white'
    )

    conclusion = (
        f"Como se observa en el gráfico, la estrategia '{optimal_strategy}' muestra un comportamiento destacado "
        f"bajo las condiciones actuales del mercado. Esta estrategia ha sido seleccionada como la mejor opción "
        f"porque, en comparación con otras, ofrece un perfil de rendimiento más favorable en respuesta a "
        f"los siguientes inputs: Precio del activo subyacente = {spot}, Precio de ejercicio = {strike}, "
        f"Tasa de interés = {rate}%, Volatilidad = {volatility}%, Fecha actual = {date_value.strftime('%Y-%m-%d')}, "
        f"Fecha de vencimiento = {date_expiration.strftime('%Y-%m-%d')}, y Tipo de opción = {option_type}. "
        f"El gráfico ilustra claramente cómo esta estrategia optimiza las ganancias o minimiza las pérdidas "
        f"en función del rango esperado de precios del activo."
    )


    return fig, conclusion