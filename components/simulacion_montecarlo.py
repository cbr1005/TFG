from dash import html, dcc, callback, Input, Output, State
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime

def simulate_gbm(S0, r, sigma, T, M, I):
    dt = T / M
    paths = np.zeros((M + 1, I))
    paths[0] = S0
    for t in range(1, M + 1):
        z = np.random.standard_normal(I)
        paths[t] = paths[t - 1] * np.exp((r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z)
    return paths

def monte_carlo_option_pricing(S0, E, r, sigma, T, M, I):
    paths = simulate_gbm(S0, r, sigma, T, M, I)
    S_T = paths[-1]
    call_payoff = np.maximum(S_T - E, 0)
    put_payoff = np.maximum(E - S_T, 0)
    call_price = np.exp(-r * T) * np.mean(call_payoff)
    put_price = np.exp(-r * T) * np.mean(put_payoff)
    return call_price, put_price

layout = html.Div([
    html.H1("Simulación de Monte Carlo", className="text-center title"),
    html.Div(className="input-container", children=[
        html.Div(className="input-group", children=[
            html.Label('Precio al contado inicial:', className="input-label"),
            dcc.Input(id='montecarlo-spot', type='number', placeholder='Ingrese valor inicial', className="input-field"),
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
    State('montecarlo-volatility', 'value'),
    State('montecarlo-rate', 'value'),
    State('montecarlo-date-value', 'date'),
    State('montecarlo-date-expiration', 'date'),
    State('montecarlo-num-paths', 'value')
)
def update_simulation(n_clicks, spot, volatility, rate, date_value, date_expiration, num_paths):
    if n_clicks > 0:
        missing_fields = []
        if spot is None:
            missing_fields.append("Precio al contado inicial")
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
        M = 252  # Número de pasos en el tiempo
        I = max(num_paths, 1)  # Asegurar que I sea al menos 1

        rate = rate / 100
        volatility = volatility / 100

        paths = simulate_gbm(spot, rate, volatility, T, M, I)
        strike_price = spot
        call_price, put_price = monte_carlo_option_pricing(spot, strike_price, rate, volatility, T, M, I)

        df = pd.DataFrame(paths)
        df['Día'] = np.arange(M + 1)
        df_melted = df.melt(id_vars=['Día'], var_name='Simulación', value_name='Precio')

        fig = px.line(df_melted, x='Día', y='Precio', color='Simulación', title="Simulación de Monte Carlo del Precio del Subyacente")
        fig.update_layout(xaxis_title="Días", yaxis_title="Precio", showlegend=False)

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

    # Devuelve valores por defecto cuando no se ha hecho click
    return px.line(), html.Div(), html.Div()