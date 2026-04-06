# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Build list of launch sites for dropdown (include "ALL")
site_options = [{'label': 'All Sites', 'value': 'ALL'}]
sites = spacex_df['Launch Site'].unique()
for s in sites:
    site_options.append({'label': s, 'value': s})

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),

    # TASK 1: Dropdown for Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=site_options,
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True,
                 style={'width': '80%', 'padding': '3px', 'margin': '0 auto'}),

    html.Br(),

    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Range slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                    value=[int(min_payload), int(max_payload)],
                    tooltip={"placement": "bottom", "always_visible": False},
                    allowCross=False),

    html.Br(),

    # TASK 4: Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL' or entered_site is None:
        # total successful launches per site
        df = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(df, values='class', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        # success vs failure for the selected site
        df_site = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = df_site['class'].value_counts().rename_axis('outcome').reset_index(name='count')
        outcome_counts['outcome'] = outcome_counts['outcome'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(outcome_counts, values='count', names='outcome',
                     title=f'Success vs. Failure for site {entered_site}')
    return fig

# TASK 4:
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_plot(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if entered_site == 'ALL' or entered_site is None:
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Payload vs. Outcome for All Sites',
                         labels={'class': 'Launch Outcome (1=Success, 0=Failure)'})
    else:
        df_site = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(df_site, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Payload vs. Outcome for {entered_site}',
                         labels={'class': 'Launch Outcome (1=Success, 0=Failure)'})
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
