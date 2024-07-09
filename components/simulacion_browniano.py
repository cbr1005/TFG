from dash import html, dcc, callback, Input, Output, State
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime
from components.funciones import simulate_gbm, monte_carlo_option_pricing

layout = html.Div([
    html.H1("Simulación del Movimiento Browniano Geometrico", className="text-center title"),
    html.Div(className="input-container", children=[
        html.Div(className="input-group", children=[
            html.Label('Precio del activo subyacente:', className="input-label"),
            dcc.Input(id='montecarlo-spot', type='number', placeholder='Ingrese precio del activo subyacente', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Precio del ejercicio:', className="input-label"),
            dcc.Input(id='montecarlo-strike', type='number', placeholder='Ingrese precio del ejercicio', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tasa de interés (%):', className="input-label"),
            dcc.Input(id='montecarlo-rate', type='number', placeholder='Ingrese tasa de interés', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Volatilidad (%):', className="input-label"),
            dcc.Input(id='montecarlo-volatility', type='number', placeholder='Ingrese volatilidad', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Número de simulaciones:', className="input-label"),
            dcc.Input(id='montecarlo-num-paths', type='number', placeholder='Ingrese numero de simulaciones', className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha actual:', className="input-label"),
            dcc.DatePickerSingle(id='montecarlo-date-value', date=datetime.today().date(), className="date-picker"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha de vencimiento:', className="input-label"),
            dcc.DatePickerSingle(id='montecarlo-date-expiration', date=None, className="date-picker"),
        ]),
        html.Div(id='montecarlo-error-message', className="error-message-container"),
        html.Button('Simular', id='montecarlo-button-simulate', n_clicks=0, className="calculate-button"),
    ]),
    dcc.Graph(id='montecarlo-simulation-graph', className="output-container"),
    html.Div(id='montecarlo-simulation-conclusion', className="output-container")
], className="container")

@callback(
    [Output('montecarlo-simulation-graph', 'figure'),
     Output('montecarlo-simulation-conclusion', 'children'),
     Output('montecarlo-error-message', 'children')],
    Input('montecarlo-button-simulate', 'n_clicks'),
    State('montecarlo-spot', 'value'),
    State('montecarlo-strike', 'value'),
    State('montecarlo-volatility', 'value'),
    State('montecarlo-rate', 'value'),
    State('montecarlo-date-value', 'date'),
    State('montecarlo-date-expiration', 'date'),
    State('montecarlo-num-paths', 'value')
)
def update_simulation(n_clicks, spot,strike, volatility, rate, date_value, date_expiration, num_paths):
    if n_clicks > 0:
        missing_fields = []
        if spot is None:
            missing_fields.append("Precio al contado inicial")
        if strike is None:
            missing_fields.append("Precio de ejercicio") 
        if volatility is None:
            missing_fields.append("Volatilidad")
        if rate is None:
            missing_fields.append("Tasa de interés")
        if date_value is None:
            missing_fields.append("Fecha actual")
        if date_expiration is None:
            missing_fields.append("Fecha de vencimiento")
        if num_paths is None:
            missing_fields.append("Número de simulaciones")

        if missing_fields:
            error_message = html.Div([
                html.H4("Error de entrada:", style={'color': 'red'}),
                html.P("Los siguientes campos están vacíos y son requeridos: " + ", ".join(missing_fields), style={'color': 'red'})
            ], style={'border': '2px solid red', 'padding': '10px', 'border-radius': '5px', 'margin-right': '20px'})
            return px.line(), html.Div(), error_message

        date_value = datetime.strptime(date_value, '%Y-%m-%d')
        date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d')
        if date_expiration <= date_value:
            error_message = html.Div([
                html.H4("Error de Fecha:", style={'color': 'red'}),
                html.P("La fecha de vencimiento debe ser posterior a la fecha actual.", style={'color': 'red'})
            ], style={'border': '2px solid red', 'padding': '10px', 'border-radius': '5px', 'margin-right': '20px'})
            return px.line(), html.Div(), error_message

        T = (date_expiration - date_value).days / 365
        M = 252  
        I = max(num_paths, 1)  

        rate = rate / 100
        volatility = volatility / 100

        paths = simulate_gbm(spot, rate, volatility, T, M, I)
        call_price, put_price = monte_carlo_option_pricing(spot, strike, rate, volatility, T, M, I)

        df = pd.DataFrame(paths)
        df['Día'] = np.arange(M + 1)
        df_melted = df.melt(id_vars=['Día'], var_name='Simulación', value_name='Precio')

        fig = px.line(df_melted, x='Día', y='Precio', color='Simulación', title="Simulación del movimiento Browniano geometrico del precio del subyacente")
        fig.update_layout(xaxis_title="Días hasta fecha de vencimiento", yaxis_title="Precio activo subyacente", showlegend=False)

        min_price = df_melted['Precio'].min()
        max_price = df_melted['Precio'].max()

        conclusion_text = "Analiza la variabilidad y el riesgo asociado con la opción basado en la simulación."
        conclusion = html.Div([
            html.H4("Conclusión de la Simulación:"),
            html.P(conclusion_text),
            html.P(f"El rango de precios simulados va desde {min_price:.2f} hasta {max_price:.2f}."),
            html.P(f"Precio estimado de la opción Call: {call_price:.2f}"),
            html.P(f"Precio estimado de la opción Put: {put_price:.2f}")
        ])

        return fig, conclusion, html.Div()

    return px.line(), html.Div(), html.Div()