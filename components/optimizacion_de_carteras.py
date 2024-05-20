from dash import html, dcc, callback, Input, Output, State
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.optimize import minimize
from scipy.stats import norm  


layout = html.Div([
    html.H1("Optimización de Carteras", className="text-center title"),
    html.Div(className="input-container", children=[
        html.Div(className="input-group", children=[
            html.Label('Número de Opciones:', className="input-label"),
            dcc.Input(id='opt-num-options', type='number', value=5, className="input-field"),
        ]),
        html.Button('Generar Opciones Aleatorias', id='opt-generate-options', n_clicks=0, className="calculate-button"),
    ]),
    dcc.Graph(id='opt-portfolio-chart', className="output-container"),
    html.Div(id='opt-portfolio-details', className="output-container")
], className="container")

@callback(
    [Output('opt-portfolio-chart', 'figure'),
     Output('opt-portfolio-details', 'children')],
    Input('opt-generate-options', 'n_clicks'),
    State('opt-num-options', 'value')
)
def optimize_portfolio(n_clicks, num_options):
    if n_clicks > 0:
        np.random.seed(42)
        spot_prices = np.random.uniform(50, 150, num_options)
        strike_prices = np.random.uniform(50, 150, num_options)
        volatilities = np.random.uniform(0.1, 0.5, num_options)
        rates = np.random.uniform(0.01, 0.05, num_options)
        expirations = np.random.uniform(0.1, 1, num_options)

        options = pd.DataFrame({
            'Spot': spot_prices,
            'Strike': strike_prices,
            'Volatility': volatilities,
            'Rate': rates,
            'Expiration': expirations
        })

        def option_price(row):
            S = row['Spot']
            K = row['Strike']
            sigma = row['Volatility']
            r = row['Rate']
            T = row['Expiration']
            d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
            return call_price

        options['Price'] = options.apply(option_price, axis=1)

        def portfolio_variance(weights, prices, volatilities):
            variance = np.dot(weights.T, np.dot(np.diag(volatilities**2), weights))
            return variance

        initial_weights = np.ones(num_options) / num_options
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(num_options))

        optimized = minimize(portfolio_variance, initial_weights, args=(options['Price'], options['Volatility']), method='SLSQP', bounds=bounds, constraints=constraints)

        options['Weight'] = optimized.x

        fig = px.pie(options, names='Spot', values='Weight', title='Optimized Portfolio Weights')

        details = html.Div([
            html.H4("Detalles de la Optimización:"),
            html.P(f"Varianza de la cartera optimizada: {optimized.fun:.4f}"),
            html.P(f"Pesos optimizados: {', '.join([f'{weight:.2f}' for weight in optimized.x])}")
        ])

        return fig, details
    
    return px.pie(), html.Div()
