import plotly.express as px
import plotly.io as pio
import pandas as pd
import numpy as np
from prophet import Prophet
import logging
import plotly.graph_objs as go
import plotly.io as pio
import time
import pandas as pd
import numpy as np
import datetime
import random
from dateutil.relativedelta import relativedelta
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# logging.getLogger('cmdstanpy').setLevel(logging.WARNING)


def create_time_series(selected_reporting_entiy):
    time_series = []
    y_value = 1000
    for reporting_entity in [1000, 2000, 3000, 4000, 5000]:
        for month in range(48):
            date = (datetime.datetime(2019, 1, 1) +
                    relativedelta(months=+month)).strftime('%Y-%m-%d')
            jump = random.choice([random.uniform(1, 2), random.uniform(
                4, 50)]) * random.choice([2, 1, 1, 55])
            y_value += jump
            time_series.append(
                {"reportingEntity": reporting_entity, "ds": date, "y": int(y_value)})
    df = pd.DataFrame(time_series)
    df = df[df['reportingEntity'] == selected_reporting_entiy]
    return df


def perform_forecasting(df):
    m = Prophet(seasonality_mode="multiplicative",
                growth='linear',
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.10,
                interval_width=0.95).fit(df)
    future = m.make_future_dataframe(periods=0, freq='ME')
    forecast = m.predict(future)

    # Convert 'ds' column to datetime
    forecast['ds'] = pd.to_datetime(forecast['ds'])

    # Join forecast and df dataframes together on 'ds' column
    forecast = pd.concat([forecast, df.drop(['ds'], axis=1)], axis=1)
    # forecast.reset_index(inplace=True)
    return forecast


def generate_chart():

    # Calculate total report count
    total_report_count = forecast['yhat'].sum()

    # Get the 'yhat' value for the last month
    last_month_yhat = forecast['yhat'].iloc[-1]

    # Calculate the change in monthly reporting
    change_in_monthly_reporting = forecast['yhat'].iloc[-1] - \
        forecast['yhat'].iloc[-2]

    # Determine the color based on the change
    color = "green" if change_in_monthly_reporting >= 0 else "red"

    fig = make_subplots(rows=1, cols=2, subplot_titles=(
        "Total Report Count", "Change in Monthly Reporting"), specs=[[{'type': 'domain'}, {'type': 'domain'}]])

    fig.add_trace(go.Indicator(
        mode="number",
        title={"text": "Current Month Count", 'font': {'size': 20}},
        value=forecast['yhat'].iloc[-1],

        gauge={'axis': {'visible': False}}
    ), row=1, col=1)

    fig.add_trace(go.Indicator(
        mode="delta",

        title={"text": "Current Compared to Last", 'font': {'size': 20}},
        value=change_in_monthly_reporting,
        number={'font': {'size': 30}},
        delta={'reference': 0, 'increasing': {
            'color': color}, 'decreasing': {'color': color}}
    ), row=1, col=2)

    # Remove the margin
    fig.update_layout(
        autosize=False,
        margin=go.layout.Margin(l=0, r=0, b=0, t=0),
        height=200,  # Set the height of the figure,
    )

    return fig


def graph_forecast(forecast):
    # Identify points outside the expected range
    forecast['outlier'] = (forecast['y'] < forecast['yhat_lower']) | (
        forecast['y'] > forecast['yhat_upper'])
    # Create a scatter plot for the forecast
    fig = go.Figure()

    # Set the background color to white
    fig.update_layout(plot_bgcolor='white',
                      # paper_bgcolor='white'
                      )

    fig.add_trace(go.Scatter(x=forecast['ds'],
                             y=forecast['yhat'],
                             mode='lines',
                             hovertemplate='<b>Date</b>: %{x}<br>' +
                             '<b>Report Count</b>: %{y}<br>',
                             name='Estimated'))
    fig.add_trace(go.Scatter(x=forecast['ds'],
                             y=forecast['yhat_upper'],
                             mode='lines',
                             name='yhat_upper',
                             showlegend=False,
                             hoverinfo='none',
                             line=dict(width=0)))
    fig.add_trace(go.Scatter(x=forecast['ds'],
                             y=forecast['yhat_lower'],
                             mode='lines',
                             name='yhat_lower',
                             showlegend=False,
                             hoverinfo='none',
                             line=dict(width=0)))
    fig.add_trace(go.Scatter(x=forecast['ds'],
                             y=forecast['y'],
                             mode='markers',
                             hovertemplate='<b>Date</b>: %{x}<br>' +
                             '<b>Report Count</b>: %{y}<br>',
                             name='Report Count',
                             marker=dict(color='black',
                                         size=4)))

    # Add markers for the outliers
    outliers = forecast[forecast['outlier']]
    fig.add_trace(go.Scatter(x=outliers['ds'], y=forecast['y'][outliers.index], mode='markers', marker=dict(
        color='rgb(255, 69, 0)', size=5),  hovertemplate='<b>Date</b>: %{x}<br>'+'<b>Report Count</b>: %{y}<br>', name='Report Count'))

    # Fill the area between yhat_upper and yhat_lower with the same color
    fig.update_traces(fill='tonexty', fillcolor='rgba(173,216,230,0.5)',
                      selector=dict(name='yhat_lower'))

    # Set the range of the y-axis to start at 0 and end at 10% more than the top 'y' value
    max_y = max(forecast['y'])
    fig.update_yaxes(range=[0, max_y + 0.15 * max_y])

    # Remove the background shading but leave the grid lines
    # fig.update_layout( paper_bgcolor='white')

    # Change the grid lines to be light grey
    fig.update_xaxes(gridcolor='lightgrey')
    fig.update_yaxes(gridcolor='lightgrey')

    # Add "Report Count" to the y-axis
    fig.update_yaxes(title_text="Report Count")

    # Add an overall trend line as a dotted line
    # fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['trend'], mode='lines', line=dict(dash='dot'), name='Overall Trend'))

    # Convert the datetime objects to the number of seconds since the Unix epoch
    # forecast['ds_seconds'] = (pd.to_datetime(forecast['ds']) -
    #                          pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')

    # Remove duplicate keys by aggregating the values using sum()
    # forecast = forecast.groupby('ds_seconds').sum().reset_index()
    # Fit a line to the data
    # slope, intercept = np.polyfit(forecast['ds_seconds'], forecast['y'], 1)
    # line = slope * forecast['ds_seconds'] + intercept
    # Add the line to the plot
    # fig.add_trace(go.Scatter(x=forecast['ds'],
    #                         y=line,
    #                         mode='lines',
    #                         hoverinfo='none',
    #                         name='Regression Line',
    #                         line=dict(dash='dot', color='rgba(255,0,0,0.2)')
    #                         ))

    fig.update_layout(
        height=400,
        plot_bgcolor='white',
        margin=go.layout.Margin(l=0, r=0, b=5, t=5)
    )

    # Remove the legend
    fig.update_layout(showlegend=False)

    return fig


def generate_table(df):

    # | label: fig-table
    # Convert 'ds' to datetime format
    df['ds'] = pd.to_datetime(df['ds'])

    # Create a pivot table
    pivot_table = df.pivot_table(
        values='y', index=df['ds'].dt.month, columns=df['ds'].dt.year, aggfunc='sum')

    # Replace NaN values with 0
    pivot_table.fillna(0, inplace=True)

    # Format the pivot table
    pivot_table.index = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                         'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    pivot_table.columns = pivot_table.columns.astype(str)
    pivot_table = pivot_table.rename_axis(
        "Report Count (by Month & Year)", axis="columns")
    styled_table = pivot_table.round(2).style.format("{:,.0f}")

    return styled_table


def graph_forecast_test(forecast, reporting_entity_id):
    # Identify points outside the expected range
    forecast['outlier'] = (forecast['y'] < forecast['yhat_lower']) | (
        forecast['y'] > forecast['yhat_upper'])
    # Create a scatter plot for the forecast
    fig = go.Figure()

    # Set the background color to white
    fig.update_layout(plot_bgcolor='white',
                      # paper_bgcolor='white'
                      )

    fig.add_trace(go.Scatter(x=forecast['ds'],
                             y=forecast['yhat'],
                             mode='lines',
                             hovertemplate='<b>Date</b>: %{x}<br>' +
                             '<b>Report Count</b>: %{y}<br>',
                             name='Estimated'))
    fig.add_trace(go.Scatter(x=forecast['ds'],
                             y=forecast['yhat_upper'],
                             mode='lines',
                             name='yhat_upper',
                             showlegend=False,
                             hoverinfo='none',
                             line=dict(width=0)))
    fig.add_trace(go.Scatter(x=forecast['ds'],
                             y=forecast['yhat_lower'],
                             mode='lines',
                             name='yhat_lower',
                             showlegend=False,
                             hoverinfo='none',
                             line=dict(width=0)))
    fig.add_trace(go.Scatter(x=forecast['ds'],
                             y=forecast['y'],
                             mode='markers',
                             hovertemplate='<b>Date</b>: %{x}<br>' +
                             '<b>Report Count</b>: %{y}<br>',
                             name='Report Count',
                             marker=dict(color='black',
                                         size=4)))

    # Add markers for the outliers
    outliers = forecast[forecast['outlier']]
    fig.add_trace(go.Scatter(x=outliers['ds'], y=forecast['y'][outliers.index], mode='markers', marker=dict(
        color='rgb(255, 69, 0)', size=5),  hovertemplate='<b>Date</b>: %{x}<br>'+'<b>Report Count</b>: %{y}<br>', name='Report Count'))

    # Fill the area between yhat_upper and yhat_lower with the same color
    fig.update_traces(fill='tonexty', fillcolor='rgba(173,216,230,0.5)',
                      selector=dict(name='yhat_lower'))

    # Set the range of the y-axis to start at 0 and end at 10% more than the top 'y' value
    max_y = max(forecast['y'])
    fig.update_yaxes(range=[0, max_y + 0.15 * max_y])

    # Remove the background shading but leave the grid lines
    # fig.update_layout( paper_bgcolor='white')

    # Change the grid lines to be light grey
    fig.update_xaxes(gridcolor='lightgrey')
    fig.update_yaxes(gridcolor='lightgrey')

    # Add "Report Count" to the y-axis
    fig.update_yaxes(title_text="Report Count")

    # Add an overall trend line as a dotted line
    # fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['trend'], mode='lines', line=dict(dash='dot'), name='Overall Trend'))

    # Convert the datetime objects to the number of seconds since the Unix epoch
    # forecast['ds_seconds'] = (pd.to_datetime(forecast['ds']) -
    #                          pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')

    # Remove duplicate keys by aggregating the values using sum()
    # forecast = forecast.groupby('ds_seconds').sum().reset_index()
    # Fit a line to the data
    # slope, intercept = np.polyfit(forecast['ds_seconds'], forecast['y'], 1)
    # line = slope * forecast['ds_seconds'] + intercept
    # Add the line to the plot
    # fig.add_trace(go.Scatter(x=forecast['ds'],
    #                         y=line,
    #                         mode='lines',
    #                         hoverinfo='none',
    #                         name='Regression Line',
    #                         line=dict(dash='dot', color='rgba(255,0,0,0.2)')
    #                         ))

    # Dummy pie chart
    fig2 = go.Figure(data=go.Pie(labels=['A', 'B', 'C'], values=[
                     10, 15, 7],  showlegend=False))

# Create subplots: 1 row, 2 columns
    figFinal = make_subplots(rows=2, cols=4, specs=[[{'type': 'xy', 'colspan': 4}, None, None, None],
                                                    [{'type': 'domain'}, {
                                                        'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}]
                                                    ],
                             row_heights=[0.67, 0.33]
                             )

    # Adding traces to subplots
# Adding all traces from fig to the first subplot
    for trace in fig.data:
        figFinal.add_trace(trace, row=1, col=1)

    figFinal.add_trace(fig2.data[0], row=2, col=1)

    figFinal.update_layout(
        title={
            'text': "Reporting Entity : " + str(reporting_entity_id),
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)  # Increase font size
        },
        height=950,
        plot_bgcolor='white',
        margin=go.layout.Margin(l=200, r=200, b=10, t=150),
    )
    figFinal.update_xaxes(gridcolor='lightgrey', row=1, col=1)
    figFinal.update_yaxes(gridcolor='lightgrey', row=1, col=1)

    # Remove the legend
    figFinal.update_layout(showlegend=False)

    figFinal.add_annotation(
        dict(
            x=0.5,
            y=-0.1,
            xref='paper',
            yref='paper',
            text="Your footer text here",
            showarrow=False,
            font=dict(size=14),
            align='center'
        )
    )

   # Dummy gauge chart
    fig3 = go.Figure(go.Indicator(
        mode="number",
        value=450,
        title={'text': "Metric Value"},
        domain={'x': [0, 1], 'y': [0, 1]}
    ))

# Adding the gauge chart to the second row, second column
    figFinal.add_trace(fig3.data[0], row=2, col=2)


# Different type of gauge chart
    fig4 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=300,
        delta={'reference': 400},
        title={'text': "Monthly Reporting"},
        gauge={'axis': {'range': [None, 500]}},
        domain={'x': [0, 1], 'y': [0, 1]}
    ))

# Adding the gauge chart to the second row, third column
    figFinal.add_trace(fig4.data[0], row=2, col=3)

# Dummy table

    fig5 = go.Figure(data=[go.Table(
        header=dict(values=['A', 'B', 'C'],
                    fill_color='grey',
                    align='left'),
        cells=dict(values=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                   fill_color='white',
                   align='left'))
    ])

# Adding the table to the second row, fourth column
    figFinal.add_trace(fig5.data[0], row=2, col=4)

    from datetime import datetime

# Get current date and time
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

# Add generation date time to the bottom right hand side of the chart
    figFinal.add_annotation(
        dict(
            x=1,
            y=-0.5,
            xref='paper',
            yref='paper',
            text="Generated on: " + date_time,
            showarrow=False,
            font=dict(size=14),
            align='right'
        )
    )

    return figFinal
