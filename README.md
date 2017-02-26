##TimeSeriesConnect
- finding connections between time series of financial instruments
- use for economic research, market, or trading strategy research
- wrapper over pandas_datareader.data.DataReader and quandl.get

1. Install (Python 3.5)
    
    ```
    sudo apt-get install libssl-dev
    python3 -m pip install virtualenv
    ```

    ```
    virtualenv venv
    cd venv/bin && source activate
    ```

    ```
    pip install -r requirements.txt    
    ```

2. Examples

    ```python
    from tsc import TSCPairs
    conn = TSCPairs(['XOM', 'CL'], 2010)

    conn.plot()
    conn.correlate()
    conn.plot_volatility()
    ```

    ```python
    from tsc import TSCBatch
    bat = TSCBatch(['XOM', 'CVX', 'XLE', 'WEC'], 2012)

    bat.plot()
    ```
