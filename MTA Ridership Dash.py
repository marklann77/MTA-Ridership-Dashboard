# Import required libraries
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load data (make sure df_monthly is defined in the same script)
df = pd.read_csv("/Users/marklannaman/Downloads/Analysis Tools/Python/MTA Ridership Mini Project/MTA_Daily_Ridership_Data__2020_-_2025_20250304.csv") 
df['Date'] = pd.to_datetime(df['Date'])  # Convert date column to datetime
df_monthly = df.resample('M', on='Date').sum().reset_index()  # Resample to monthly totals

# Add season classification
df_monthly['Season'] = df_monthly['Date'].dt.month.map(
    lambda x: 'Winter' if x in [12, 1, 2] else 'Summer' if x in [6, 7, 8] else 'Other'
)

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div(children=[
    
    # Title
    html.H1("NYC Subway Ridership Dashboard", style={'textAlign': 'center'}),

    # Dropdown for Year Selection
    html.Label("Select Year:"),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': str(year), 'value': year} for year in df_monthly['Date'].dt.year.unique()],
        value=df_monthly['Date'].dt.year.min(),  # Default to first year
        clearable=False
    ),

    # Line Chart
    dcc.Graph(id='ridership-trend'),

    # Bar Chart
    dcc.Graph(id='seasonal-ridership')
])

# Callback to update the ridership trend line chart
@app.callback(
    Output('ridership-trend', 'figure'),
    Input('year-dropdown', 'value')
)
def update_line_chart(selected_year):
    filtered_df = df_monthly[df_monthly['Date'].dt.year == selected_year]
    fig = px.line(filtered_df, x='Date', y='Subways: Total Estimated Ridership',
                  title=f"NYC Subway Ridership Trend ({selected_year})",
                  labels={'Subways: Total Estimated Ridership': 'Total Ridership'},
                  template="plotly_dark")
    return fig

# Callback to update the seasonal bar chart
@app.callback(
    Output('seasonal-ridership', 'figure'),
    Input('year-dropdown', 'value')
)
def update_bar_chart(selected_year):
    filtered_df = df_monthly[df_monthly['Date'].dt.year == selected_year]
    season_avg = filtered_df.groupby('Season')['Subways: Total Estimated Ridership'].mean().reset_index()
    
    fig = px.bar(season_avg, x='Season', y='Subways: Total Estimated Ridership',
                 title=f"Average Ridership by Season ({selected_year})",
                 labels={'Subways: Total Estimated Ridership': 'Avg Monthly Ridership'},
                 template="plotly_dark",
                 color='Season')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

