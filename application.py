# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px


# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)
server=app.server
# Create an app layout
app.layout = html.Div(
    children=[
        html.H1('SpaceX Launch Records Dashboard',
                style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
        html.Br(),
        html.Div([
            dcc.Dropdown(
                id='site-dropdown',
                options=[
                    {'label': 'All Sites', 'value': 'ALL'},
                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                ],
                value='ALL',
                placeholder="Select a Launch Site",
                searchable=True
            ),
        ]),
        html.Div(dcc.Graph(id='success-pie-chart')),
        html.Br(),
        html.P("Payload range (Kg):"),
        html.Div(
            dcc.RangeSlider(
                id='sliderid',
                min=min_payload, max=max_payload, step=1000,
                marks={min_payload: str(min_payload), max_payload: str(max_payload)},
                value=[min_payload, max_payload]
            )
        ),
        html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    ]
)

# Add a callback function for `site-dropdown` as input and `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        all_sites_counts = spacex_df['Launch Site'].value_counts()
        pie_fig = px.pie(
            values=all_sites_counts.values,
            names=all_sites_counts.index,
            title='Total Success Launches By Site'
        )
        return pie_fig
    else:
        site_filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        class_counts = site_filtered_df['class'].value_counts()
        pie_fig = px.pie(
            values=class_counts.values,
            names=class_counts.index,
            title=f'Total Success Launches for Site - {entered_site}'
        )
        return pie_fig

# Add a callback function for `site-dropdown` and `sliderid` as inputs and `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='sliderid', component_property='value')
)
def get_scatter(entered_site, payload_range):
    if entered_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) &
                                (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    scatter_fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category"
    )
    return scatter_fig

# Run the app
if __name__ == '__main__':
    app.run_server()