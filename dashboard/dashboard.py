from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import requests
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor

app = Dash(__name__)

API_BASE = 'https://us-county-health-api.onrender.com'

# Fetch measures from Flask API
response = requests.get(f'{API_BASE}/api/measures')
measures = response.json()
measure_options = [{'label': m['measure_name'], 'value': m['measure_name']} for m in measures]

app.layout = html.Div([
    html.H1("US County Health Analysis"),
    
    html.Div([
        html.Label("Select a Measure:"),
        dcc.Dropdown(
            id='measure-dropdown',
            options=measure_options,
            value=measures[0]['measure_name']
        )
    ]),

    html.Div(id='charts-container')
])

@app.callback(
    Output('charts-container', 'children'),
    Input('measure-dropdown', 'value')
)
def update_charts(measure_name):
    # Fetch all chart data in parallel
    with ThreadPoolExecutor() as executor:
        by_state_future = executor.submit(requests.get, f'{API_BASE}/api/measures/{measure_name}/by_state')
        trend_future = executor.submit(requests.get, f'{API_BASE}/api/measures/{measure_name}/trend')

    bar_response = by_state_future.result()
    trend_response = trend_future.result()
    map_response = by_state_future.result()

    # Process bar chart data
    bar_data = pd.DataFrame(bar_response.json())
    bar_data = bar_data[~bar_data['state_name'].isin(['PR', 'DC'])]
    bar_data['avg_value'] = pd.to_numeric(bar_data['avg_value'])
    bar_data = bar_data.sort_values('avg_value', ascending=False).head(10)
    
    bar_chart = px.bar(
        bar_data,
        x='state_name',
        y='avg_value',
        title=f'Top 10 States — {measure_name}'
    )
    
    # Fetch trend data
    # Not excluding PR and DC from trend data as it is national level data
    trend_data = pd.DataFrame(trend_response.json())
    trend_data['avg_value'] = pd.to_numeric(trend_data['avg_value'])
    
    line_chart = px.line(
        trend_data,
        x='year_start',
        y='avg_value',
        title=f'National Trend — {measure_name}'
    )

    # Fetch data for map
    map_data = pd.DataFrame(map_response.json())

    # Exclude Puerto Rico (PR) and Washington, D.C. (DC) from the map
    map_data = map_data[~map_data['state_name'].isin(['PR', 'DC'])]

    # Ensure avg_value is numeric for the choropleth
    map_data['avg_value'] = pd.to_numeric(map_data['avg_value'])

    choropleth = px.choropleth(
        map_data,
        locations='state_name',
        locationmode='USA-states',
        color='avg_value',
        scope='usa',
        title=f'{measure_name} by State',
        color_continuous_scale='Reds'
    )
    
    return [
        dcc.Graph(figure=bar_chart),
        dcc.Graph(figure=line_chart),
        dcc.Graph(figure=choropleth)
    ]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))