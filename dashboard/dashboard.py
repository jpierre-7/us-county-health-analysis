from dash import Dash, html, dcc, Input, Output, callback_context
import plotly.express as px
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import pandas as pd
import os
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Dash(__name__, title="US County Health Analysis")
server = app.server  # Expose WSGI server

API_BASE = os.environ.get('API_BASE', 'https://us-county-health-api.onrender.com')

# Configure a resilient requests session with automatic retries and backoff
def create_resilient_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

http_session = create_resilient_session()

def fetch_json(url, timeout=30):
    """Safely fetch and parse JSON from a given URL with timeout and JSONDecode protection."""
    try:
        response = http_session.get(url, timeout=timeout)
        if response.status_code == 200:
            try:
                return response.json(), None
            except (ValueError, requests.exceptions.JSONDecodeError) as err:
                logger.error(f"Failed to parse JSON from {url}: {err}. Response text preview: {response.text[:200]}")
                return None, "Invalid JSON received from server."
        else:
            try:
                err_data = response.json()
                err_msg = err_data.get('message') or err_data.get('error') or f"HTTP {response.status_code}"
            except Exception:
                err_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            return None, err_msg
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP request failed for {url}: {e}")
        return None, str(e)


def serve_layout():
    """Generates the layout dynamically on each page load/refresh."""
    measures_data, error_msg = fetch_json(f'{API_BASE}/api/measures', timeout=15)

    if measures_data and isinstance(measures_data, list) and len(measures_data) > 0:
        measure_options = [{'label': m['measure_name'], 'value': m['measure_name']} for m in measures_data]
        default_measure = measures_data[0]['measure_name']
        warning_banner = None
    else:
        measure_options = []
        default_measure = None
        warning_banner = html.Div(
            [
                html.H4("⚠️ Service Notice: Connecting to Backend API / Database..."),
                html.P(
                    f"Details: {error_msg or 'No measures data available'}. "
                    "On Render's free tier, sleeping services take 30–60 seconds to wake up. "
                    "Please wait a moment and refresh or reselect a measure."
                ),
            ],
            id="service-warning",
            style={
                'backgroundColor': '#fff3cd',
                'color': '#856404',
                'padding': '15px',
                'borderRadius': '6px',
                'marginBottom': '20px',
                'border': '1px solid #ffeeba'
            }
        )

    return html.Div(
        [
            html.H1("US County Health Analysis", style={'textAlign': 'center', 'marginBottom': '25px'}),
            *( [warning_banner] if warning_banner else [] ),
            html.Div(
                [
                    html.Label("Select a Health Measure:", style={'fontWeight': 'bold', 'fontSize': '16px'}),
                    dcc.Dropdown(
                        id='measure-dropdown',
                        options=measure_options,
                        value=default_measure,
                        placeholder="Select a measure..."
                    )
                ],
                style={'maxWidth': '600px', 'margin': '0 auto 25px auto'}
            ),
            dcc.Loading(
                id="loading-charts",
                type="default",
                children=html.Div(id='charts-container')
            )
        ],
        style={'fontFamily': 'system-ui, -apple-system, sans-serif', 'padding': '20px', 'maxWidth': '1200px', 'margin': '0 auto'}
    )

app.layout = serve_layout

@app.callback(
    Output('charts-container', 'children'),
    Input('measure-dropdown', 'value')
)
def update_charts(measure_name):
    if not measure_name:
        return html.Div(
            html.P("Please select a measure to view charts.", style={'textAlign': 'center', 'color': '#6c757d', 'fontSize': '16px'}),
            style={'padding': '40px'}
        )

    # Fetch all chart data in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        by_state_future = executor.submit(fetch_json, f'{API_BASE}/api/measures/{measure_name}/by_state')
        trend_future = executor.submit(fetch_json, f'{API_BASE}/api/measures/{measure_name}/trend')

    by_state_data, by_state_err = by_state_future.result()
    trend_data_list, trend_err = trend_future.result()

    if by_state_err or trend_err or not by_state_data or not trend_data_list:
        errors = [err for err in [by_state_err, trend_err] if err]
        return html.Div(
            [
                html.H4("⚠️ Error Loading Chart Data"),
                html.P(f"Failed to retrieve data for '{measure_name}'. The API or Supabase database may be temporarily waking up."),
                html.Small(f"Details: {'; '.join(errors) if errors else 'No data returned'}")
            ],
            style={
                'backgroundColor': '#f8d7da',
                'color': '#721c24',
                'padding': '15px',
                'borderRadius': '6px',
                'marginTop': '20px',
                'border': '1px solid #f5c6cb'
            }
        )

    # Process bar chart data
    bar_data = pd.DataFrame(by_state_data)
    if 'state_name' in bar_data.columns and 'avg_value' in bar_data.columns:
        bar_data = bar_data[~bar_data['state_name'].isin(['PR', 'DC'])]
        bar_data['avg_value'] = pd.to_numeric(bar_data['avg_value'], errors='coerce')
        bar_data = bar_data.dropna(subset=['avg_value']).sort_values('avg_value', ascending=False).head(10)
        
        bar_chart = px.bar(
            bar_data,
            x='state_name',
            y='avg_value',
            title=f'Top 10 States — {measure_name}',
            labels={'state_name': 'State', 'avg_value': 'Average Value'}
        )
    else:
        bar_chart = px.bar(title=f'Top 10 States — {measure_name} (No data)')

    # Fetch trend data (national level, PR & DC retained)
    trend_df = pd.DataFrame(trend_data_list)
    if 'year_start' in trend_df.columns and 'avg_value' in trend_df.columns:
        trend_df['avg_value'] = pd.to_numeric(trend_df['avg_value'], errors='coerce')
        trend_df = trend_df.dropna(subset=['avg_value']).sort_values('year_start', ascending=True)
        line_chart = px.line(
            trend_df,
            x='year_start',
            y='avg_value',
            title=f'National Trend — {measure_name}',
            labels={'year_start': 'Year', 'avg_value': 'Average Value'}
        )
    else:
        line_chart = px.line(title=f'National Trend — {measure_name} (No data)')

    # Process choropleth map data
    map_data = pd.DataFrame(by_state_data)
    if 'state_name' in map_data.columns and 'avg_value' in map_data.columns:
        map_data = map_data[~map_data['state_name'].isin(['PR', 'DC'])]
        map_data['avg_value'] = pd.to_numeric(map_data['avg_value'], errors='coerce')
        map_data = map_data.dropna(subset=['avg_value'])

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
