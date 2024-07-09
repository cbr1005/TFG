from dash import dcc, html, Input, Output, State, callback, ALL
import plotly.graph_objs as go
import numpy as np
from datetime import datetime
from components.funciones import function_option_price



layout = html.Div([
    html.Div([
        html.H3("Comparación de Simulaciones de Opciones por Volatilidad", style={'textAlign': 'center'}),
        html.Div([
            html.Div(className="input-group", children=[
                html.Label('Precio del activo subyacente:', className="input-label"),
                dcc.Input(id='spot_price', type='number', placeholder='Ingrese el precio del activo subyacente', className="input-field"),
            ]),
            html.Div(className="input-group", children=[
                html.Label('Precio del ejercicio:', className="input-label"),
                dcc.Input(id='strike_price', type='number', placeholder='Ingrese el precio del ejercicio', className="input-field"),
            ]),
            html.Div(className="input-group", children=[
                html.Label('Tasa de interés (%):', className="input-label"),
                dcc.Input(id='interest_rate', type='number', placeholder='Ingrese la tasa de interés', className="input-field"),
            ]),
            html.Div(className="input-group", children=[
                html.Label('Fecha actual:', className="input-label"),
                dcc.DatePickerSingle(id='comp-date-value', date=datetime.today().date(), className="date-picker"),
            ]),
            html.Div(className="input-group", children=[
                html.Label('Fecha de vencimiento:', className="input-label"),
                dcc.DatePickerSingle(id='comp-date-expiration', date=None, className="date-picker"),
            ]),
            html.Div(id='error-message-com', className="error-message-container"),  
            html.Div(className="input-group", children=[
                html.Label('Tipo de opción:', className="input-label"),
                dcc.Dropdown(
                    id='option_type',
                    options=[
                        {'label': 'Call', 'value': 'call'},
                        {'label': 'Put', 'value': 'put'}
                    ],
                    value='call',
                    className="dropdown"
                ),
            ]),
        ], className='input-container'),
        html.Div([
            html.Button('Añadir Volatilidad', id='add_volatility', n_clicks=0, className='calculate-button'),
            html.Button('Comparar', id='compare', n_clicks=0, className='calculate-button'),
        ], style={'textAlign': 'center', 'marginTop': '20px'}),
        html.Div(id='volatility_inputs', children=[]),
    ]),
    dcc.Graph(id='option_prices_graph'),
    html.Div(id='conclusions', className='output-container')
], className="container")


@callback(
    Output('volatility_inputs', 'children'),
    Input('add_volatility', 'n_clicks'),
    State('volatility_inputs', 'children')
)
def add_volatility_input(n_clicks, children):
    new_element = html.Div([
        dcc.Input(
            id={'type': 'volatility_input', 'index': n_clicks},
            type='number', placeholder='Volatilidad %',
            style={'marginRight': '5px', 'width': '200px'}
        )
    ])
    children.append(new_element)
    return children

def apply_visual_offset(prices, index):
    """ Aplica un pequeño offset visual a los precios para evitar superposiciones en el gráfico. """
    offset = index * 0.05 * max(prices) 
    return [price + offset for price in prices]


@callback(
    [Output('option_prices_graph', 'figure'),
     Output('conclusions', 'children'),
     Output('error-message-com', 'children')], 
    Input('compare', 'n_clicks'),
    State({'type': 'volatility_input', 'index': ALL}, 'value'),
    State('spot_price', 'value'), State('strike_price', 'value'),
    State('interest_rate', 'value'), State('comp-date-value', 'date'),
    State('comp-date-expiration', 'date'), State('option_type', 'value')
)
def update_graphs(n_clicks, volatilities, spot, strike, rate, val_date, exp_date, opt_type):
    if n_clicks == 0:
        return go.Figure(), [], html.Div()  

    if not all([spot, strike, rate, val_date, exp_date, opt_type]):
        error_message = html.Div([
            html.H4("Error de entrada:", style={'color': 'red'}),
            html.P("Todos los campos deben estar completos antes de comparar.", style={'color': 'red'})
        ], style={'border': '2px solid red', 'padding': '10px', 'border-radius': '5px'})
        return go.Figure(), [], error_message

    val_date = datetime.strptime(val_date, '%Y-%m-%d')
    exp_date = datetime.strptime(exp_date, '%Y-%m-%d')
    if exp_date <= val_date:
        error_message = html.Div([
            html.H4("Error de Fecha:", style={'color': 'red'}),
            html.P("La fecha de vencimiento debe ser posterior a la fecha actual.", style={'color': 'red'})
        ], style={'border': '2px solid red', 'padding': '10px', 'border-radius': '5px'})
        return go.Figure(), [], error_message

    T = (exp_date - val_date).days / 365.25
    rate = rate / 100

    fig = go.Figure()
    spot_prices = np.linspace(spot * 0.5, spot * 1.5, 100)

    volatilities = [float(vol) / 100 for vol in volatilities if vol]  
    for index, vol in enumerate(volatilities):
        prices = [function_option_price(s, strike, rate, T, vol, opt_type) for s in spot_prices]
        adjusted_prices = apply_visual_offset(prices, index)
        fig.add_trace(go.Scatter(x=spot_prices, y=adjusted_prices, mode='lines', name=f'Vol: {vol * 100:.2f}%'))

    fig.update_layout(title='Valor de Opción por Precio del Activo Subyacente',
                      xaxis_title='Precio del Activo Subyacente',
                      yaxis_title='Valor de la Opción')
    return fig, [], html.Div() 