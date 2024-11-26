import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from media_framing_analysis import ConflictFramingAnalyzer
import pandas as pd
import os
import json
from datetime import datetime, timedelta

# Initialize the app
app = dash.Dash(__name__, title='Media Framing Analysis Dashboard')

# Initialize analyzer
analyzer = ConflictFramingAnalyzer(newsapi_key=os.getenv('NEWS_API_KEY'))

def load_latest_results():
    """Load the most recent analysis results"""
    results_dir = 'analysis_results'
    results_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
    if not results_files:
        return None
    
    latest_file = max(results_files, key=lambda x: os.path.getctime(os.path.join(results_dir, x)))
    with open(os.path.join(results_dir, latest_file), 'r') as f:
        return json.load(f)

app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # updates every 30 seconds
        n_intervals=0
    ),
    
    html.H1('Media Framing Analysis Dashboard', 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    html.Div([
        html.Div([
            html.H3('Overall Sentiment Distribution', style={'textAlign': 'center'}),
            dcc.Graph(id='sentiment-distribution')
        ], style={'flex': '50%', 'padding': '10px'}),
        
        html.Div([
            html.H3('Mention Frequency Over Time', style={'textAlign': 'center'}),
            dcc.Graph(id='mention-frequency')
        ], style={'flex': '50%', 'padding': '10px'})
    ], style={'display': 'flex', 'marginBottom': '20px'}),
    
    html.Div([
        html.H3('Source Distribution', style={'textAlign': 'center'}),
        dcc.Graph(id='source-distribution')
    ], style={'marginBottom': '20px'}),
    
    html.Div([
        html.H3('Key Terms Analysis', style={'textAlign': 'center'}),
        dcc.Graph(id='key-terms')
    ], style={'marginBottom': '20px'})
], style={'fontFamily': 'Arial, sans-serif', 'margin': '20px', 'backgroundColor': '#f5f6fa'})

@app.callback(
    [Output('sentiment-distribution', 'figure'),
     Output('mention-frequency', 'figure'),
     Output('source-distribution', 'figure'),
     Output('key-terms', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(_):
    results = load_latest_results()
    if not results:
        return [{} for _ in range(4)]
    
    # Sentiment Distribution
    sentiment_data = {
        'Category': ['Israel Positive', 'Israel Negative', 'Palestine Positive', 'Palestine Negative'],
        'Count': [
            results['overall_stats']['israel_positive'],
            results['overall_stats']['israel_negative'],
            results['overall_stats']['palestine_positive'],
            results['overall_stats']['palestine_negative']
        ]
    }
    sentiment_fig = px.bar(
        sentiment_data,
        x='Category',
        y='Count',
        color='Category',
        title='Sentiment Distribution'
    )
    
    # Mention Frequency
    mention_data = pd.DataFrame(results['time_series'])
    mention_fig = px.line(
        mention_data,
        x='date',
        y=['israel_mentions', 'palestine_mentions'],
        title='Mention Frequency Over Time'
    )
    
    # Source Distribution
    sources = pd.DataFrame(results['source_stats'].items(), columns=['Source', 'Count'])
    source_fig = px.pie(
        sources,
        values='Count',
        names='Source',
        title='Distribution of News Sources'
    )
    
    # Key Terms
    terms_data = pd.DataFrame([
        {'term': term, 'count': count}
        for term, count in results['key_terms'].items()
    ]).sort_values('count', ascending=True).tail(15)
    
    terms_fig = px.bar(
        terms_data,
        x='count',
        y='term',
        orientation='h',
        title='Most Frequent Key Terms'
    )
    
    return sentiment_fig, mention_fig, source_fig, terms_fig

if __name__ == '__main__':
    app.run_server(debug=True)
