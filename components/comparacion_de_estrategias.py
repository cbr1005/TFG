from dash import html, dcc, callback, Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime
from components.funciones import calcular_opcion_estandar_precio
import dash

layout = html.Div([
    html.H1("Comparación de Estrategias de Opciones", className="text-center title"),
    html.Div(className="input-container", children=[
        html.Div(className="input-group", children=[
            html.Label('Precio al contado:', className="input-label"),
            dcc.Input(id='comp-spot', type='number', placeholder='Ingrese el precio al contado inicial', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Precio de ejercicio:', className="input-label"),
            dcc.Input(id='comp-strike', type='number', placeholder='Ingrese el precio de ejercicio', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tasa de interés (%):', className="input-label"),
            dcc.Input(id='comp-rate', type='number',placeholder='Ingrese la tasa de interes', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Volatilidad (%):', className="input-label"),
            dcc.Input(id='comp-volatility', type='number', placeholder='Ingrese la volatilidad', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha actual:', className="input-label"),
            dcc.DatePickerSingle(id='comp-date-value', date='2024-05-01', className="date-picker"),
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
    html.Div(className="button-container", style={'display': 'flex', 'justify-content': 'center', 'gap': '10px', 'margin-top': '20px'}, children=[
        html.Button('Straddle', id='toggle-straddle', n_clicks=0, className="calculate-button"),
        html.Button('Strangle', id='toggle-strangle', n_clicks=0, className="calculate-button"),
        html.Button('Bull Spread', id='toggle-bull-spread', n_clicks=0, className="calculate-button"),
        html.Button('Bear Spread', id='toggle-bear-spread', n_clicks=0, className="calculate-button"),
        html.Button('Butterfly Spread', id='toggle-butterfly-spread', n_clicks=0, className="calculate-button"),
        html.Button('Iron Condor', id='toggle-iron-condor', n_clicks=0, className="calculate-button")
    ]),
    dcc.Graph(id='comp-strategy-comparison-graph', className="output-container"),
    html.Div(id='comp-strategy-comparison-conclusion', className="output-container")
], className="container")

def determine_optimal_strategy(spot, strike, rate, volatility, date_value, date_expiration, option_type):
    # Define thresholds for volatility and price change expectations
    high_volatility_threshold = 25
    low_volatility_threshold = 15
    # Calculate expected price movement
    expected_price_movement = volatility * np.sqrt((date_expiration - date_value).days / 365)
    if volatility > high_volatility_threshold:
        if abs(expected_price_movement) > 0.1 * spot:
            return 'Straddle'
        else:
            return 'Strangle'
    elif volatility < low_volatility_threshold:
        if abs(expected_price_movement) < 0.1 * spot:
            return 'Butterfly Spread'
        else:
            return 'Iron Condor'
    else:
        if spot < strike:
            return 'Bear Spread'
        else:
            return 'Bull Spread'

@callback(
    [Output('comp-strategy-comparison-graph', 'figure'),
     Output('comp-strategy-comparison-conclusion', 'children')],
    [Input('comp-button-compare', 'n_clicks'),
     Input('toggle-straddle', 'n_clicks'),
     Input('toggle-strangle', 'n_clicks'),
     Input('toggle-bull-spread', 'n_clicks'),
     Input('toggle-bear-spread', 'n_clicks'),
     Input('toggle-butterfly-spread', 'n_clicks'),
     Input('toggle-iron-condor', 'n_clicks')],
    [State('comp-spot', 'value'),
     State('comp-strike', 'value'),
     State('comp-rate', 'value'),
     State('comp-volatility', 'value'),
     State('comp-date-value', 'date'),
     State('comp-date-expiration', 'date'),
     State('comp-option-type', 'value')]
)
def compare_strategies(n_clicks, n_straddle, n_strangle, n_bull_spread, n_bear_spread, n_butterfly_spread, n_iron_condor,
                       spot, strike, rate, volatility, date_value, date_expiration, option_type):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if not n_clicks:
        return go.Figure(), html.Div()  # No action on initial load

    if triggered_id == 'comp-button-compare' and not all([spot, strike, rate, volatility, date_value, date_expiration, option_type]):
        return go.Figure(), html.Div([
            html.H4("Error de Entrada:"),
            html.P("Por favor, complete todos los campos antes de comparar estrategias.")
        ])

    date_value = datetime.strptime(date_value, '%Y-%m-%d') if date_value else datetime.now()
    date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d') if date_expiration else datetime.now() + pd.Timedelta(days=365)

    spot_prices = np.linspace(spot * 0.5, spot * 1.5, 100) if spot else np.linspace(100, 200, 100)
    strategies = {'Straddle': [], 'Strangle': [], 'Bull Spread': [], 'Bear Spread': [], 'Butterfly Spread': [], 'Iron Condor': []}

    for s in spot_prices:
        call_atm = calcular_opcion_estandar_precio(s, strike, rate / 100, date_value, date_expiration, volatility / 100, 'call')[0][0]
        put_atm = calcular_opcion_estandar_precio(s, strike, rate / 100, date_value, date_expiration, volatility / 100, 'put')[0][0]

        strategies['Straddle'].append(call_atm + put_atm)
        strategies['Strangle'].append(call_atm * 0.9 + put_atm * 1.1)
        strategies['Bull Spread'].append(call_atm - calcular_opcion_estandar_precio(s, strike * 1.1, rate / 100, date_value, date_expiration, volatility / 100, 'call')[0][0])
        strategies['Bear Spread'].append(put_atm - calcular_opcion_estandar_precio(s, strike * 0.9, rate / 100, date_value, date_expiration, volatility / 100, 'put')[0][0])
        strategies['Butterfly Spread'].append(call_atm * 0.9 + call_atm * 1.1 - 2 * call_atm)
        strategies['Iron Condor'].append((put_atm * 0.9 - put_atm * 0.8) + (call_atm * 1.1 - call_atm * 1.2))

    optimal_strategy = determine_optimal_strategy(spot, strike, rate, volatility, date_value, date_expiration, option_type)

    df = pd.DataFrame(strategies, index=spot_prices)
    fig = go.Figure()

    strategy_toggle_states = [n_straddle, n_strangle, n_bull_spread, n_bear_spread, n_butterfly_spread, n_iron_condor]
    strategies_list = ['Straddle', 'Strangle', 'Bull Spread', 'Bear Spread', 'Butterfly Spread', 'Iron Condor']

    for strategy, toggle, color in zip(strategies_list, strategy_toggle_states, ['blue', 'green', 'orange', 'purple', 'cyan', 'magenta']):
        if triggered_id == 'comp-button-compare' or toggle % 2 != 0:
            fig.add_trace(go.Scatter(x=df.index, y=df[strategy], mode='lines', name=strategy, line=dict(color=color, width=2 if strategy != optimal_strategy else 4)))

    if optimal_strategy:
        fig.add_trace(go.Scatter(x=df.index, y=df[optimal_strategy], mode='lines', name=f'Optimal: {optimal_strategy}', line=dict(color='red', width=4)))

    fig.update_layout(title='Comparación de Estrategias de Opciones', xaxis_title='Precio Spot', yaxis_title='Valor de la Estrategia')

    conclusion = html.Div([
        html.H4("Conclusión de la Comparación de Estrategias:"),
        html.P(f"La estrategia más óptima para las condiciones dadas es '{optimal_strategy}', destacada en el gráfico en rojo y con un grosor superior para indicar su potencial superior bajo las condiciones actuales.")
    ])

    return fig, conclusion