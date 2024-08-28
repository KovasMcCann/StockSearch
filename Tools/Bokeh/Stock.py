from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.io import curdoc
import requests
from datetime import datetime

curdoc().theme = 'dark_minimal'

# Create a ColumnDataSource with initial empty data
data_source = ColumnDataSource(data={"Close": [], "DateTime": []})

# Create a figure object
fig = figure(
    x_axis_type="datetime", 
    width=950,  # Use 'width' instead of 'plot_width'
    height=450,  # Use 'height' instead of 'plot_height'
    tooltips=[("Close", "@Close")], 
    title="Bitcoin Close Price Live (Every Second)"
)

# Add a line renderer with the data source
fig.line(
    x="DateTime", 
    y="Close", 
    line_color="tomato", 
    line_width=3.0, 
    source=data_source
)

# Set x-axis and y-axis labels
fig.xaxis.axis_label = "Date"
fig.yaxis.axis_label = "Price ($)"

# Define the callback function to update the chart
def update_chart():
    global data_source
    try:
        # Fetch the latest Bitcoin price
        resp = requests.get("https://generic709.herokuapp.com/stockc/msft")
        resp.raise_for_status()  # Raise an exception for HTTP errors
        hist_data = resp.json()
        # Create new data row
        new_row = {
            "Price": [hist_data["price"]],
            "DateTime": [datetime.now()]
        }
        # Update the data source with new data
        data_source.stream(new_row, rollover=200)  # Limit the number of points to 200
    except Exception as e:
        print(f"Error fetching data: {e}")

# Add a periodic callback to update the chart every second
curdoc().add_periodic_callback(update_chart, 1000)

# Add the figure to the current document
curdoc().add_root(fig)
