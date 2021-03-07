# REF: https://labs.ig.com/rest-trading-api-reference


class BaseUrl:
    """
    DO NOT CHANGE
    """
    def __init__(self):
        self.protocol = "https://"

        # Don't change this to point to demo-url, code will prepend 'demo' if demo account is chosen
        self.base = "api.ig.com/gateway/deal/"

        # TODO: Move these out to separate lib package
        self.stream_session = '/lightstreamer/create_session.txt'
        self.stream_control = '/lightstreamer/control.txt'
