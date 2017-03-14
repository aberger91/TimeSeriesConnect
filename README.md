##Time Series Connections
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
    python setup.py install
    ```
##Frame
1. light wrapper over pd.DataFrame to access market data
2. instantiate with a product code, start, and end date
3. user methods include frame (full dataset) and series (specific column)

##Batch
2. access for multiple frames 
