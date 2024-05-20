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
            html.Label('Precio al contado:', className="input-label"),
            dcc.Input(id='montecarlo-spot', type='number', value=100, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Volatilidad (%):', className="input-label"),
            dcc.Input(id='montecarlo-volatility', type='number', value=20, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Tasa de interes (%):', className="input-label"),
            dcc.Input(id='montecarlo-rate', type='number', value=2, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Número de rutas:', className="input-label"),
            dcc.Input(id='montecarlo-num-paths', type='number', value=10, min=1, max=15, step=1, className="input-field"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha actual:', className="input-label"),
            dcc.DatePickerSingle(id='montecarlo-date-value', date='2024-05-01', className="date-picker"),
        ]),
        html.Div(className="input-group", children=[
            html.Label('Fecha de vencimiento:', className="input-label"),
            dcc.DatePickerSingle(id='montecarlo-date-expiration', date='2024-11-01', className="date-picker"),
        ]),
        html.Button('Simular', id='montecarlo-button-simulate', n_clicks=0, className="calculate-button"),
    ]),
    dcc.Graph(id='montecarlo-simulation-graph', className="output-container"),
    html.Div(id='montecarlo-simulation-conclusion', className="output-container")
], className="container")

@callback(
    [Output('montecarlo-simulation-graph', 'figure'),
     Output('montecarlo-simulation-conclusion', 'children')],
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
        date_value = datetime.strptime(date_value, '%Y-%m-%d')
        date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d')
        T = (date_expiration - date_value).days / 365
        M = 252  # Número de pasos en el tiempo (supongamos 252 días de trading en un año)
        I = min(max(num_paths, 1), 10)  # Asegurar que I esté entre 1 y 10

        # Convertir tasas a decimales
        rate = rate / 100
        volatility = volatility / 100

        # Simular caminos de GBM
        paths = simulate_gbm(spot, rate, volatility, T, M, I)

        # Calcular precios de opciones
        strike_price = spot  # Puedes ajustar esto según tus necesidades
        call_price, put_price = monte_carlo_option_pricing(spot, strike_price, rate, volatility, T, M, I)

        # Convertir los datos en un DataFrame de pandas para Plotly
        df = pd.DataFrame(paths)
        df['Día'] = np.arange(M + 1)

        # Reestructurar el DataFrame para Plotly
        df_melted = df.melt(id_vars=['Día'], var_name='Simulación', value_name='Precio')

        # Crear la gráfica
        fig = px.line(df_melted, x='Día', y='Precio', color='Simulación', title="Simulación de Monte Carlo del Precio del Subyacente")
        fig.update_layout(xaxis_title="Días", yaxis_title="Precio", showlegend=False)

        # Calcular el rango de precios
        min_price = df_melted['Precio'].min()
        max_price = df_melted['Precio'].max()

        # Conclusión personalizada
        if max_price - min_price > spot * 0.5:
            conclusion_text = "La simulación muestra una alta variabilidad en los precios del subyacente, lo que sugiere un alto riesgo asociado con esta opción."
        elif max_price - min_price > spot * 0.2:
            conclusion_text = "La simulación indica una moderada variabilidad en los precios del subyacente, lo que sugiere un riesgo moderado."
        else:
            conclusion_text = "La simulación muestra una baja variabilidad en los precios del subyacente, lo que sugiere un bajo riesgo asociado con esta opción."

        conclusion = html.Div([
            html.H4("Conclusión de la Simulación:"),
            html.P(conclusion_text),
            html.P(f"El rango de precios simulados va desde {min_price:.2f} hasta {max_price:.2f}. Esto implica que el precio del subyacente podría experimentar "
                   f"cambios significativos antes de la fecha de vencimiento, afectando el valor de la opción."),
            html.P(f"Precio estimado de la opción Call: {call_price:.2f}"),
            html.P(f"Precio estimado de la opción Put: {put_price:.2f}")
        ])

        return fig, conclusion

    return px.line(), html.Div()
