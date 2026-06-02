from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import requests

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
    # Fetch data from Flask API
    response = requests.get(f'http://localhost:5000/api/measures/{measure_name}/by_state')
    data = response.json()
    
    import pandas as pd
    df = pd.DataFrame(data).head(10).sort_values('avg_value', ascending=False)
    
    bar_chart = px.bar(
        df,
        x='state_name',
        y='avg_value',
        title=f'Top 10 States — {measure_name}'
    )
    
    return dcc.Graph(figure=bar_chart)

if __name__ == '__main__':
    app.run(debug=True, port=8050)