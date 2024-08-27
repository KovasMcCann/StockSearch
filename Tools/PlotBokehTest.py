import pandas as pd
import pickle
import redis
from bokeh.plotting import figure, show, curdoc
from bokeh.models import ColumnDataSource, HoverTool, TextInput, Div
from bokeh.layouts import column, row
from bokeh.events import KeyPress

# Redis Config
redis_host = '10.1.10.121'  # Replace with '127.0.0.1' if necessary
redis_port = 6379
redis_db = 2  # default database
redis_password = None  # no password set
r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

# Function to plot the data
def plot(data):
    if data is None:
        print("No data to plot.")
        return None

    df = pd.DataFrame(data)

    # Convert 'index' to datetime and 'row' to the actual values
    df['row'] = df['row'].astype(str)
    df['Open'] = df['row'].str.extract(r'Open\s+([0-9\.e+-]+)')[0].astype(float)

    # Filter to keep only 'Open' values
    df = df[['index', 'Open']]
    df.set_index('index', inplace=True)

    # Prepare Bokeh data source
    source = ColumnDataSource(df.reset_index())

    # Create a Bokeh plot
    p = figure(x_axis_type='datetime', title='Open Prices Over Time', width=800, height=400, tools="pan,wheel_zoom,box_zoom,reset")
    p.line(x='index', y='Open', source=source, line_width=2, color='blue', legend_label='Open Price')
    p.circle(x='index', y='Open', source=source, size=8, color='blue', legend_label='Open Price')

    # Add hover tool
    hover = HoverTool()
    hover.tooltips = [("Date", "@index{%F}"), ("Open Price", "@Open")]
    hover.formatters = {'@index': 'datetime'}
    p.add_tools(hover)

    # Dark theme
    p.title.text_font_size = '16pt'
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Open Price'
    p.xaxis.major_label_orientation = 'vertical'
    p.grid.grid_line_alpha = 0.3
    p.background_fill_color = '#2F2F2F'
    p.border_fill_color = '#2F2F2F'
    p.axis.axis_line_color = 'white'
    p.axis.major_label_color = 'white'
    p.grid.grid_line_color = '#555555'

    return p

# Function to load data
def load(ticker):
    data = r.hget(f'{ticker}', 'Data')
    if data:
        try:
            # Deserialize DataFrame from binary data
            data = pickle.loads(data)
        except (pickle.UnpicklingError, TypeError) as e:
            # Handle errors and log them
            print(f"Error during unpickling: {e}")
            data = None
    return data

# Function to fetch tickers from Redis
def fetch_tickers():
    tickers = r.keys('Data')  # Retrieve all keys with the prefix 'Data'
    tickers = [ticker.decode('utf-8') for ticker in tickers]  # Decode byte keys to strings
    return tickers

# Filter tickers based on input
def filter_tickers(search_text):
    tickers = fetch_tickers()
    filtered = [ticker for ticker in tickers if search_text.lower() in ticker.lower()]
    return filtered

# Update ticker list based on search input
def update_ticker_list(attr, old, new):
    search_text = text_input.value
    filtered_tickers = filter_tickers(search_text)
    ticker_list_div.text = "<br>".join(filtered_tickers) if filtered_tickers else "No matches found."

# Initialize components
text_input = TextInput(title="Search Ticker:", value="")
text_input.on_change('value', update_ticker_list)

ticker_list_div = Div(text="")

# Initial plot
initial_ticker = fetch_tickers()[0] if fetch_tickers() else None
initial_data = load(initial_ticker) if initial_ticker else None
initial_plot = plot(initial_data)

# Callback for ticker selection
def ticker_selected(event):
    ticker = event.item
    data = load(ticker)
    new_plot = plot(data)
    if new_plot:
        layout.children[1] = new_plot

# Create a dummy div to show a placeholder ticker for selection (in a real implementation, use a more interactive widget)
ticker_list_div.on_click(ticker_selected)

# Layout and add to document
layout = column(text_input, ticker_list_div, initial_plot)
curdoc().add_root(layout)
