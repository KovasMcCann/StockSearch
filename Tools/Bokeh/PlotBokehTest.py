import pickle
import redis
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, HoverTool
from prompt_toolkit import prompt
import pandas as pd

# Redis Config
redis_host = '10.1.10.121'  # Replace with '127.0.0.1' if necessary
redis_port = 6379
redis_db = 2  # default database
redis_password = None  # no password set
r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

def plot(data):
    if data is None:
        print("No data to plot.")
        return

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
    p = figure(x_axis_type='datetime', title='Open Prices Over Time', width=800, height=400)
    p.line(x='index', y='Open', source=source, line_width=2, color='blue', legend_label='Open Price')
    p.circle(x='index', y='Open', source=source, size=8, color='blue', legend_label='Open Price')

    # Add hover tool
    hover = HoverTool()
    hover.tooltips = [("Date", "@index{%F}"), ("Open Price", "@Open")]
    hover.formatters = {'@index': 'datetime'}
    p.add_tools(hover)

    p.title.text_font_size = '16pt'
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Open Price'
    p.xaxis.major_label_orientation = 'vertical'
    p.grid.grid_line_alpha = 0.3

    # Show plot in a browser
    show(p)

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

def main():
    ticker = 'aapl'
    if ticker:
        data = load(ticker)
        plot(data)
    else:
        print("No ticker symbol entered.")

if __name__ == "__main__":
    main()
