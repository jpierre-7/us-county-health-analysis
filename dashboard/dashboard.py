from dash import Dash, html

app = Dash(__name__)

app.layout = html.Div([
    html.H1("US County Health Analysis")
])

if __name__ == '__main__':
    app.run(debug=True, port=8050)