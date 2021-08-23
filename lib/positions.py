# REF: https://labs.ig.com/rest-trading-api-reference


class Positions:
    """
    DO NOT CHANGE
    Adding is ok ... and encouraged ;)
    """
    base = {
        'path': 'positions/',
        'GET': {
            'version': '2',
            'tokens': True
        }
    }

    trade = {
        'path': 'positions/otc',
        'DELETE': {
            'version': '1',
            'tokens': True
        },
        'POST': {
            'version': '2',
            'tokens': True
        }
    }
