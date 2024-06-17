from dash import dcc, html, Input, Output, State, callback, ALL
import plotly.graph_objs as go
import numpy as np
import pandas as pd
from datetime import datetime
from components.funciones import calcular_opcion_estandar_precio
from app import app

layout = html.Div([
    html.Div([
        html.H3("Comparación de Simulaciones de Opciones por Volatilidad", style={'textAlign': 'center'}),
        html.Div([
            html.Div(className="input-group", children=[
                html.Label('Precio al contado inicial:', className="input-label"),
                dcc.Input(id='spot_price', type='number', placeholder=' Ingrese el precio al contado inicial', className="input-field"),
            ]),
            html.Div(className="input-group", children=[
                html.Label('Precio de ejercicio:', className="input-label"),
                dcc.Input(id='strike_price', type='number', placeholder=' Ingrese el precio de ejercicio', className="input-field"),
            ]),
            html.Div(className="input-group", children=[
                html.Label('Tasa de interés (%):', className="input-label"),
            dcc.Input(id='interest_rate', type='number',placeholder='Ingrese la tasa de interes', className="input-field"),
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

@callback(
    [Output('option_prices_graph', 'figure'),
     Output('conclusions', 'children')],
    Input('compare', 'n_clicks'),
    State({'type': 'volatility_input', 'index': ALL}, 'value'),
    State('spot_price', 'value'), State('strike_price', 'value'),
    State('interest_rate', 'value'), State('comp-date-value', 'date'),
    State('comp-date-expiration', 'date'), State('option_type', 'value')
)
def update_graphs(n_clicks, volatilities, spot, strike, rate, val_date, exp_date, opt_type):
    if n_clicks > 0:
        fig = go.Figure()
        val_date = datetime.strptime(val_date, '%Y-%m-%d')
        exp_date = datetime.strptime(exp_date, '%Y-%m-%d')
        spot_prices = np.linspace(spot * 0.5, spot * 1.5, 100)
        conclusions = []

        for vol in filter(None, volatilities):
            vol = float(vol) / 100
            prices = [calcular_opcion_estandar_precio(s, strike, rate / 100, val_date, exp_date, vol, opt_type)[0][0] for s in spot_prices]
            fig.add_trace(go.Scatter(x=spot_prices, y=prices, mode='lines', name=f'Vol: {vol * 100}%'))

            conclusion_text = (
                f"Para una volatilidad de {vol * 100}%, el precio de la opción varía significativamente a medida que el precio del activo subyacente "
                f"cambia. Esto se debe a que una mayor volatilidad generalmente aumenta el valor de las opciones, ya que hay más probabilidad de que "
                f"la opción termine en el dinero (ITM). En este caso, hemos analizado cómo esta volatilidad específica afecta el precio de la opción "
                f"desde un precio del activo subyacente de {spot * 0.5:.2f} hasta {spot * 1.5:.2f}. Observa cómo las curvas de precios responden a "
                f"cambios en el precio del activo subyacente, reflejando el impacto de la volatilidad en el valor de la opción."
            )

            conclusions.append(html.Div([
                html.H4(f"Conclusión para Volatilidad {vol * 100}%:"),
                html.P(conclusion_text)
            ]))

        fig.update_layout(title='Valor de Opción por Precio del Activo Subyacente',
                          xaxis_title='Precio del Activo Subyacente',
                          yaxis_title='Valor de la Opción')

        return fig, conclusions
    
    return go.Figure(), []
