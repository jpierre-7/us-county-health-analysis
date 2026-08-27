from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import requests
import pandas as pd
import os
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Dash(__name__)

API_BASE = os.environ.get('API_BASE', 'https://us-county-health-api.onrender.com')

def fetch_json(url, timeout=15):
    """Safely fetch and parse JSON from a given URL."""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return response.json(), None
        else:
            try:
                err_data = response.json()
                err_msg = err_data.get('message') or err_data.get('error') or f"HTTP {response.status_code}"
            except Exception:
                err_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            return None, err_msg
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        return None, str(e)

# Fetch measures from Flask API safely on startup
initial_measures, initial_error = fetch_json(f'{API_BASE}/api/measures')

if initial_measures and isinstance(initial_measures, list) and len(initial_measures) > 0:
    measure_options = [{'label': m['measure_name'], 'value': m['measure_name']} for m in initial_measures]
    default_measure = initial_measures[0]['measure_name']
    startup_warning = None
else:
    measure_options = []
    default_measure = None
    startup_warning = html.Div(
        [
            html.H4("⚠️ Service Notice: Could not connect to API/Database"),
            html.P(f"Details: {initial_error or 'No measures found'}. If the database was sleeping, it may take 30-60 seconds to wake up. Please refresh the page.")
        ],
        style={
            'backgroundColor': '#fff3cd',
            'color': '#856404',
            'padding': '15px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'border': '1px solid #ffeeba'
        }
    )

app.layout = html.Div([
    html.H1("US County Health Analysis"),
    *( [startup_warning] if startup_warning else [] ),
    html.Div([
        html.Label("Select a Measure:"),
        dcc.Dropdown(
            id='measure-dropdown',
            options=measure_options,
            value=default_measure,
            placeholder="Select a measure..."
        )
    ]),

    html.Div(id='charts-container')
])

@app.callback(
    Output('charts-container', 'children'),
    Input('measure-dropdown', 'value')
)
def update_charts(measure_name):
    if not measure_name:
        return html.Div(
            html.P("Please select a measure to view charts."),
            style={'padding': '20px', 'color': '#6c757d'}
        )

    # Fetch all chart data in parallel
    with ThreadPoolExecutor() as executor:
        by_state_future = executor.submit(fetch_json, f'{API_BASE}/api/measures/{measure_name}/by_state')
        trend_future = executor.submit(fetch_json, f'{API_BASE}/api/measures/{measure_name}/trend')

    by_state_data, by_state_err = by_state_future.result()
    trend_data_list, trend_err = trend_future.result()

    if by_state_err or trend_err or not by_state_data or not trend_data_list:
        errors = [err for err in [by_state_err, trend_err] if err]
        return html.Div(
            [
                html.H4("⚠️ Error Loading Chart Data"),
                html.P(f"Failed to retrieve data for '{measure_name}'. The API or Supabase database may be temporarily sleeping or unavailable."),
                html.Small(f"Details: {'; '.join(errors) if errors else 'No data returned'}")
            ],
            style={
                'backgroundColor': '#f8d7da',
                'color': '#721c24',
                'padding': '15px',
                'borderRadius': '5px',
                'marginTop': '20px',
                'border': '1px solid #f5c6cb'
            }
        )

    # Process bar chart data
    bar_data = pd.DataFrame(by_state_data)
    if 'state_name' in bar_data.columns and 'avg_value' in bar_data.columns:
        bar_data = bar_data[~bar_data['state_name'].isin(['PR', 'DC'])]
        bar_data['avg_value'] = pd.to_numeric(bar_data['avg_value'])
        bar_data = bar_data.sort_values('avg_value', ascending=False).head(10)
        
        bar_chart = px.bar(
            bar_data,
            x='state_name',
            y='avg_value',
            title=f'Top 10 States — {measure_name}'
        )
    else:
        bar_chart = px.bar(title=f'Top 10 States — {measure_name} (No data)')

    # Fetch trend data
    # Not excluding PR and DC from trend data as it is national level data
    trend_df = pd.DataFrame(trend_data_list)
    if 'year_start' in trend_df.columns and 'avg_value' in trend_df.columns:
        trend_df['avg_value'] = pd.to_numeric(trend_df['avg_value'])
        line_chart = px.line(
            trend_df,
            x='year_start',
            y='avg_value',
            title=f'National Trend — {measure_name}'
        )
    else:
        line_chart = px.line(title=f'National Trend — {measure_name} (No data)')

    # Fetch data for map
    map_data = pd.DataFrame(by_state_data)
    if 'state_name' in map_data.columns and 'avg_value' in map_data.columns:
        # Exclude Puerto Rico (PR) and Washington, D.C. (DC) from the map
        map_data = map_data[~map_data['state_name'].isin(['PR', 'DC'])]
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
    else:
        choropleth = px.choropleth(title=f'{measure_name} by State (No data)')

    return [
        dcc.Graph(figure=bar_chart),
        dcc.Graph(figure=line_chart),
        dcc.Graph(figure=choropleth)
    ]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
