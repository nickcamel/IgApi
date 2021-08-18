# REF: https://labs.ig.com/rest-trading-api-reference


class Positions:
    """
    DO NOT CHANGE
    Adding is ok ... and encouraged ;)
    """
    base = {}
    epic = {  # should change name of field.. don't use epic.. doesn't make sens
        'path': 'positions/',
        'GET': {
            'version': '2',
            'tokens': True
        },
        'DELETE': {
            'version': '1',
            'tokens': True
        },
        'POST': {
            'version': '2',
            'tokens': True
        }
    }
