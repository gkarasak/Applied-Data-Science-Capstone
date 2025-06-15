import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# -----------------------------------------------------------------------------
# data
# -----------------------------------------------------------------------------
spacex_df = pd.read_csv("spacex_launch_dash.csv")
# compute min/max payload for slider
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# -----------------------------------------------------------------------------
# app initialization
# -----------------------------------------------------------------------------
app = dash.Dash(__name__)
server = app.server  # for deployment

# -----------------------------------------------------------------------------
# layout
# -----------------------------------------------------------------------------
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    
    # TASK 1: Launch Site Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                [{'label': site, 'value': site} 
                 for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),
    
    # TASK 2: Success Pie Chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    html.P("Payload range (Kg):"),
    
    # TASK 3: Payload Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={0: '0', 2500: '2.5k', 5000: '5k',
               7500: '7.5k', 10000: '10k'},
        value=[min_payload, max_payload]
    ),
    html.Br(),
    
    # TASK 4: Success‐Payload Scatter Chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# -----------------------------------------------------------------------------
# callbacks
# -----------------------------------------------------------------------------

# TASK 2 callback: update pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(selected_site):
    if selected_site == 'ALL':
        # show total success counts for all sites
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Total Success Launches by Site'
        )
    else:
        # filter dataframe for the selected site
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        # count success vs. failure
        counts = df_site['class'].value_counts().reset_index()
        counts.columns = ['class', 'count']
        counts['class'] = counts['class'].map({0: 'Failure', 1: 'Success'})
        fig = px.pie(
            counts,
            names='class',
            values='count',
            title=f'Success vs. Failure for site {selected_site}'
        )
    return fig

# TASK 4 callback: update scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def get_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    # filter by payload first
    df_payload = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    if selected_site == 'ALL':
        df_scatter = df_payload
        title = 'Payload vs. Outcome for All Sites'
    else:
        df_scatter = df_payload[df_payload['Launch Site'] == selected_site]
        title = f'Payload vs. Outcome for site {selected_site}'
    
    fig = px.scatter(
        df_scatter,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title,
        labels={'class': 'Launch Outcome'}
    )
    return fig

# -----------------------------------------------------------------------------
# run
# -----------------------------------------------------------------------------
if __name__ == '__main__':
       app.run(debug=True, port=8051)


