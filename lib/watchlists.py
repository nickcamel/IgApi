# REF: https://labs.ig.com/rest-trading-api-reference


class Watchlists:
    """
    DO NOT CHANGE
    Adding is ok ... and encouraged ;)
    """
    base = {
        'path': 'watchlists',
        'GET': {
            'version': '1',
            'tokens': True,
        }
        # Not supported yet: 'POST'
    }

    id = {
        'path': 'watchlists/',
        'GET': {
            'version': '1',
            'tokens': True,
        }
        # Not supported yet: 'PUT', 'DELETE'
    }
