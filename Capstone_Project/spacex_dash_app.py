#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpaceX Launch Analytics Dashboard (Dash)
Tasks covered:
- TASK 1: Launch Site Drop-down Input Component
- TASK 2: Callback for success-pie-chart
- TASK 3: Payload Range Slider
- TASK 4: Callback for success-payload-scatter-chart
---

## How to Run

1. **Prepare the data file**

   Place a CSV named **`spacex_launch_dash.csv`** in the same folder as the script.
   The file must contain the following columns:

   * `Launch Site`
   * `class`
   * `Payload Mass (kg)`
   * `Booster Version Category`

2. **Run the application**

   Open a terminal and execute:

   ```bash
   pip install dash plotly pandas
   python spacex_dash_app.py
   ```

3. **View the dashboard**

   Once the app starts, open the URL shown in the terminal (usually):
   
   [http://127.0.0.1:8050/](http://127.0.0.1:8050/)

---
"""

import os
import pandas as pd
from dash import Dash, dcc, html, Output, Input
import plotly.express as px

# --- Data loading ---
# Expect a CSV "spacex_launch_dash.csv" with the following columns:
# ['Launch Site', 'class', 'Payload Mass (kg)', 'Booster Version Category']
CSV_PATH = os.environ.get("SPACEX_DASH_CSV", "spacex_launch_dash.csv")

if os.path.exists(CSV_PATH):
    spacex_df = pd.read_csv(CSV_PATH)
else:
    raise FileNotFoundError(
        f"CSV file not found at '{CSV_PATH}'. "
        "Place 'spacex_launch_dash.csv' next to this script or set SPACEX_DASH_CSV env var."
    )

# cleanup
spacex_df = spacex_df.dropna(subset=['Launch Site', 'class', 'Payload Mass (kg)']).copy()

# Determine payload bounds for the slider
payload_min = float(spacex_df['Payload Mass (kg)'].min())
payload_max = float(spacex_df['Payload Mass (kg)'].max())

# Launch site options (+ 'All Sites')
launch_sites = sorted(spacex_df['Launch Site'].unique().tolist())
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in launch_sites
]

## Create a dash application
app = Dash(__name__)
app.title = "SpaceX Launch Analytics"

# Create an app layout
app.layout = html.Div(
    style={'fontFamily': 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif',
           'margin': '24px'},
    children=[
        html.H1("SpaceX Launch Records Dashboard", style={'textAlign': 'center'}),

        # TASK 1: Launch Site Dropdown
        html.Div([
            html.Label("Select Launch Site:", style={'fontWeight': 600}),
            dcc.Dropdown(
                id='site-dropdown',
                options=dropdown_options,
                value='ALL',                  # default
                placeholder="Select a launch site",
                clearable=False
            ),
        ], style={'maxWidth': 600, 'margin': '0 auto 24px auto'}),

        # TASK 2: Success Pie Chart
        html.Div([
            dcc.Graph(id='success-pie-chart')
        ], style={'marginBottom': '32px'}),

        # TASK 3: Payload Range Slider
        html.Div([
            html.Label("Select Payload Range (kg):", style={'fontWeight': 600}),
            dcc.RangeSlider(
                id='payload-slider',
                min=payload_min, max=payload_max, step=1000,
                value=[payload_min, payload_max],
                tooltip={'always_visible': False, 'placement': 'bottom'}
            ),
            html.Div(
                id='payload-range-text',
                style={'marginTop': '8px', 'fontSize': '14px', 'color': '#555'}
            )
        ], style={'maxWidth': 900, 'margin': '0 auto 24px auto'}),

        # TASK 4: Success vs Payload Scatter
        html.Div([
            dcc.Graph(id='success-payload-scatter-chart')
        ]),
    ]
)

# Display the current slider selection as helper text
@app.callback(
    Output('payload-range-text', 'children'),
    Input('payload-slider', 'value')
)
def _update_payload_label(range_vals):
    lo, hi = range_vals
    return f"Current range: {lo:,.0f} kg — {hi:,.0f} kg"


# TASK 2: Callback to render success-pie-chart based on site dropdown
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        # Pie of total successes per launch site
        successes_by_site = (
            spacex_df[spacex_df['class'] == 1]
            .groupby('Launch Site')['class'].count()
            .reset_index(name='Successes')
        )
        fig = px.pie(
            successes_by_site,
            values='Successes',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # Pie of success vs failure for the selected site
        site_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        outcome_counts = (
            site_df.groupby('class')['class'].count()
            .rename(index={0: 'Failure', 1: 'Success'})
            .reset_index(name='Count')
            .rename(columns={'class': 'Outcome'})
        )
        fig = px.pie(
            outcome_counts,
            values='Count',
            names='Outcome',
            title=f'Launch Outcomes for {selected_site}'
        )

    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
    return fig


# TASK 4: Callback to render scatter based on site + payload range
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter(selected_site, payload_range):
    lo, hi = payload_range
    # Filter by payload range
    mask = (spacex_df['Payload Mass (kg)'] >= lo) & (spacex_df['Payload Mass (kg)'] <= hi)

    if selected_site != 'ALL':
        mask &= (spacex_df['Launch Site'] == selected_site)

    filtered = spacex_df[mask].copy()

    # Scatter: x=payload, y=class (0/1), color by booster version category
    fig = px.scatter(
        filtered,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=(
            f"Correlation between Payload and Success "
            f"{'(All Sites)' if selected_site=='ALL' else f'({selected_site})'}"
        )
    )
    # Make y-axis show labels 0/1 as Failure/Success
    fig.update_yaxes(
        tickmode='array',
        tickvals=[0, 1],
        ticktext=['Failure (0)', 'Success (1)']
    )
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
    return fig


if __name__ == "__main__":
    # Run the app
    #app.run_server(debug=True)
    app.run(debug=True)
