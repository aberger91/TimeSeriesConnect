##TimeSeriesConnect
- finding connections between time series of financial instruments
- use for economic research, market, or trading strategy research

1. Depends:
    ```
    sudo apt-get install libssl-dev
    python3 -m pip install virtualenv
    ```

2. VirtualEnv (Python 3.5)


    ```
    virtualenv venv
    cd venv/bin && source activate
    ```

3. Install 
    ```
    pip install -r requirements.txt    
    ```

- Examples

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
