# IgApi
Rest -and streaming api for IG / IG-Labs (https://labs.ig.com/gettingstarted)

Add your IG API credentials in `api_credentials` in root folder and run `python main.py`.
Make sure the credentials in the file are valid for the account chosen in `main.py`, i.e. `demo` or `live` in call to 
`IgApi(account='<account_type')`  

## Requirements
Python 3.9 (recommended)

Python 3.7 (should work, not tested)

Note: Shebangs intentionally omitted in `main.py`, so make sure to initiate with correct python version.

## Release Notes
 

### v1.0.0
This first version acts as a good introduction to anyone who wants to further develop the code by adding features 
to existing API methods and/or adding new methods.

The infrastructure is built in such a way that the attributes of different sections/methods in 
(https://labs.ig.com/rest-trading-api-reference)
are split in to different files in `/lib`, where `/lib/ig_api.py` acts as a lib collector and is the interface to all 
methods. `main.py` in root folder demonstrates different calls to these API methods 
through `ig_api.py`.
 
Added features
- REST-API connecting, support for both `demo` and `live` accounts.
- REST-API logout
- A couple of "watchlist" commands
- Price for epic market
- Streaming API connecting (subsciption to streaming not implemented yet)

Notes: 

- The current infrastructure and wrapper methods may change in future. Reason for this is that as different methods
are implemented, one realise that the simple wrapper e.g. `IgApi.__request` or `IgApi.__get_headers`, is not sufficient 
and may prove to be too complicated to serve it's simple purpose.
- All errors lead to `sys.exit(1)` at the moment.