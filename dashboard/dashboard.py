from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import requests
import pandas as pd

app = Dash(__name__)

# Fetch measures from Flask API
response = requests.get('http://localhost:5000/api/measures')
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
    # Fetch bar chart data
    bar_response = requests.get(f'http://localhost:5000/api/measures/{measure_name}/by_state')
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
    trend_response = requests.get(f'http://localhost:5000/api/measures/{measure_name}/trend')
    trend_data = pd.DataFrame(trend_response.json())
    trend_data['avg_value'] = pd.to_numeric(trend_data['avg_value'])
    
    line_chart = px.line(
        trend_data,
        x='year_start',
        y='avg_value',
        title=f'National Trend — {measure_name}'
    )

    # Fetch data for map
    map_response = requests.get(f'http://localhost:5000/api/measures/{measure_name}/by_state')
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
    app.run(debug=True, port=8050)