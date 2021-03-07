# REF: https://labs.ig.com/rest-trading-api-reference


class Login:
    """
    DO NOT CHANGE
    Adding is ok ... and encouraged ;)
    """
    base = {
        'path': 'session',
        'POST': {
            'version': '2',
            'tokens': False,
        },
        'DELETE': {
            'version': '1',
            'tokens': True,
            'code': 204
        }
        # Not supported yet: 'GET', 'PUT'
    }
