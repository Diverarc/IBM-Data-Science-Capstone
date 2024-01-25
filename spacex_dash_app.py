# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px


# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

def clean_booster_version(original_string):
    if 'v1.0' in original_string:
        return 'v1.0'
    elif 'v1.1' in original_string:
        return 'v1.1'
    elif 'FT' in original_string:
        return 'FT'
    elif 'B4' in original_string:
        return 'B4'
    elif 'B5' in original_string:
        return 'B5'
    else:
        return original_string

# Apply the mapping function to clean the 'Booster Version' column in spacex_df
spacex_df['Booster Version'] = spacex_df['Booster Version'].apply(clean_booster_version)


# Create a dash application
app = dash.Dash(__name__)


# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=[
                                                {'label': 'All Sites', 'value': 'ALL'},
                                                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                            ],
                                            value='ALL',
                                            placeholder="Select a Launch Site here",
                                            searchable=True
                                            ),
                                html.Br(),


                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),


                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={i: str(i) for i in range(0, 10001, 1000)},
                                                value=[min_payload, max_payload]),


                                html.Br(),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(selected_site):
    # Ensure spacex_df is accessible within this scope
    global spacex_df


    if selected_site == 'ALL':
        # Calculate total success launches for each site
        site_success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='SuccessCount')


        # Calculate total success launches from all sites
        total_success_count = site_success_counts['SuccessCount'].sum()


        # Calculate the proportion of success launches for each site
        site_success_counts['Proportion'] = site_success_counts['SuccessCount'] / total_success_count


        # Render a pie chart for the proportions of success launches for all sites
        fig = px.pie(site_success_counts, values='Proportion', names='Launch Site',
                     title='Proportion of Success Launches for All Sites')
    else:
        # Filter spacex_df for the selected launch site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
       
        # Render a pie chart for the selected site
        fig = px.pie(filtered_df, names='class', title=f'Success vs Failure ({selected_site})',
                     color_discrete_map={'1': 'blue', '0': 'red'})


    return fig




# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
Output(component_id='success-payload-scatter-chart', component_property='figure'),
[Input(component_id='site-dropdown', component_property='value'),
 Input(component_id="payload-slider", component_property="value")]
)
def render_scatter_chart(selected_site, selected_payload_range):
    # Filter DataFrame based on selected launch site
    if selected_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]


    # Filter DataFrame based on selected payload range
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
                            (filtered_df['Payload Mass (kg)'] <= selected_payload_range[1])]


    # Create scatter plot
    scatter_fig = px.scatter(
    filtered_df,
    x='Payload Mass (kg)',  # Replace with your actual payload column name
    y='class',        # Replace with your actual class column name
    color='Booster Version',  # Replace with your actual booster version column name
    title='Payload vs Launch Outcome',
    labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
    hover_data={'Payload Mass (kg)': True, 'class': True, 'Booster Version': True}
    )


# Limit y-axis tickmarks to 0 and 1
    scatter_fig.update_layout(yaxis=dict(tickvals=[0, 1], ticktext=['0', '1']))








    return scatter_fig








# Run the app
if __name__ == '__main__':
    app.run_server(port=8051)





