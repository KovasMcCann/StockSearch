from bokeh.plotting import figure, show, output_file, ColumnDataSource
from bokeh.models import HoverTool
from bokeh.layouts import column
from bokeh.io import curdoc
import pandas as pd
import pickle
import redis

# Redis connection details
redis_host = '10.1.10.121'
redis_port = 6379
redis_db = 0
redis_password = None

r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

def load_data(ticker):
    data = r.hget(f'{ticker}', 'Data')
    if data:
        try:
            # Deserialize DataFrame from binary data
            data = pickle.loads(data)
        except (pickle.UnpicklingError, TypeError) as e:
            print(f"Error during unpickling: {e}")
            data = None
        return data

def plot(data):
    df = pd.DataFrame(data)
    print(df.head())  # Debugging: Print the DataFrame to inspect its structure

    if 'row' in df.columns:
        df['row'] = df['row'].astype(str)
        df['Open'] = df['row'].str.extract(r'Open\s+([0-9\.e+-]+)')[0].astype(float)
        df = df[['index', 'Open']]
        df.set_index('index', inplace=True)

        source = ColumnDataSource(data={'x': df.index, 'y': df['Open']})

        p = figure(title="Simple Scatter Plot", x_axis_label='Date', y_axis_label='Open Price', x_axis_type='datetime')
        p.line(x='x', y='y', source=source, line_width=2, color='blue', legend_label='Open Price')
        p.circle(x='x', y='y', source=source, size=8, color='blue', legend_label='Open Price')

        hover = HoverTool()
        hover.tooltips = [("Date", "@x{%F}"), ("Open Price", "@y")]
        hover.formatters = {'@x': 'datetime'}
        p.add_tools(hover)

        p.title.text_font_size = '16pt'
        p.xaxis.major_label_orientation = 'vertical'
        p.grid.grid_line_alpha = 0.3

        # Add plot to the current document
        curdoc().add_root(column(p))
    else:
        print("Error: 'row' column not found in the DataFrame")

def main():
    ticker = 'aapl'  # Example ticker symbol
    if ticker:
        data = load_data(ticker)
        if data is not None:
            plot(data)
        else:
            print("No data found for the ticker symbol.")
    else:
        print("No ticker symbol entered.")

# Run the main function
main()