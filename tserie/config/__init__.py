from .qproducts import QPRODUCT
from quandl import ApiConfig

COLUMN_NAMES = ('Adj Close', 'Settle', 'Value', 'Last')

class TSCError(Exception):
    pass
    
try:    
    ApiConfig.api_key = open('../../quandl_api.key').read().strip()
except: 
    print('''
            warning - could not load quandl api_key
            '''
            )
