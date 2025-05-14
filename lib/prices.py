# REF: https://labs.ig.com/rest-trading-api-reference


class Prices:
    """
    DO NOT CHANGE
    Adding is ok ... and encouraged ;)
    """
    base = {}
    epic = {
        'path': 'prices/',
        'GET': {
            'version': '3',
            'tokens': True,
        }
    }

    hist = {
        'path': 'prices/',
        'GET': {
            'version': '1',
            'tokens': True,
        }
    }

    market_details = {
        'path': 'markets/',
        'GET': {
            'version': '4',
            'tokens': True,
        }
    }
