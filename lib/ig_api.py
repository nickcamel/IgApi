"""
credits: https://labs.ig.com/node/557
"""
import sys
import requests
from pprint import pprint
import os

sys.path.append(os.path.dirname(__file__))
from base_url import BaseUrl
from login import Login
from prices import Prices
from watchlists import Watchlists


class IgApi:

    def __init__(self, account='demo'):
        """
        Constructor that connects to REST-API and stores tokens for future communication
        """
        self._identity = None
        self._pass = None
        self._api_key = None

        base_path = os.path.dirname(__file__)
        with open(os.path.join(base_path, os.pardir, 'api_credentials'), 'r') as f:
            for line in f:
                if 'identity' in line:
                    self._identity = line.split('=')[-1].strip()
                elif 'pass' in line:
                    self._pass = line.split('=')[-1].strip()
                elif 'api_key' in line:
                    self._api_key = line.split('=')[-1].strip()

        self.connected_rest_api = False
        self.connected_streaming_api = False

        self.url = BaseUrl()
        self.account = account
        self._auth_handshake = self.__connect()

    def markets_prices_epic(self, epic):
        """
        Gets the prices for specific market
        Default: the minute prices within the last 10 minutes
        (https://labs.ig.com/rest-trading-api-reference/service-detail?id=587)
        :param epic: (str) IG Market instrument
        :return: (json) prices
        """

        print("--- Get prices ---")
        print(f"Get prices for\t\t\t{epic}")

        rsp = self.__request(Prices.epic, method='GET', url_append=epic)

        rsp_json = rsp.json()
        pprint(rsp_json)

        return rsp_json

    @staticmethod
    def get_market_epic_from_watchlist(watchlist, market_string):
        print("--- Get market epic ---")
        epic = ""
        try:
            for market in watchlist['markets']:
                if market['instrumentName'] == market_string:
                    epic = market['epic']
                    print(f"Found epic in market: {market_string}:{epic}")
                    break
        except KeyError as e:
            print("Error: expected keys incorrect")
            print(e)
            sys.exit(1)

        if not epic:
            print(f"Warning: no epic or market not found: {market_string}")
            sys.exit(1)

        return epic

    def watchlists_id(self, id):
        """
        Get details surrounding specific watchlist
        :param id: (int/string) Watchlist identifier
        :return: (json) Watchlist details
        """

        print("--- Get Watchlist ---")
        print(f"id\t\t\t\t{id}")

        rsp = self.__request(Watchlists.id, method='GET', url_append=id)
        body = rsp.json()
        pprint(body)

        return body

    def watchlists(self, list_name=""):
        """
        Prints all watchlists and returns id for "list_name"
        :param list_name: (str) watchlist to return id for (default empty, no id is returned)
        :return:
        """
        print("--- Get Watchlists ---")
        rsp = self.__request(base=Watchlists.base, method='GET')

        body = rsp.json()
        pprint(body)
        print()
        id = ""

        # This snippet has nothing to do with the REST-API, .. just being handy
        # Get the id of watchlist
        if list_name:
            print(f"Searching watchlist\t\t{list_name}")
            id = ""
            try:
                for elem in body['watchlists']:
                    if elem['name'] == list_name:
                        id = elem['id']
                        print(f"Found watchlist:\t\t{list_name}:{id}")
                        break
            except KeyError as e:
                print("Error: missing key or element")
                print(e)
                sys.exit(1)

            if not id:
                print("Error: Did not find watchlist id for {list_name}")
                sys.exit(1)

        return body, id

    def __connect(self):
        """
        Method creates authenticated connection to REST-API
        :return: json response
        """
        print("\n--- Connecting ---")
        if self.connected_rest_api:
            print("Warning: rest api seems connected already. Log out first")
            return

        # Get url to connection endpoint

        # body
        body = dict()
        body["identifier"] = self._identity
        body["password"] = self._pass

        # make the POST request
        rsp = self.__request(base=Login.base, method='POST', body=body)

        auth_rsp = self.__validate_auth_response(rsp)

        self.connected_rest_api = True
        print("--- Rest api connected ---\n")
        return auth_rsp

    def connect_streaming_api(self):
        print("--- Connecting to streaming api ---")

        if not self.connected_rest_api:
            print("Warning: REST-API not connected. Cannot proceed")
            return None

        if self.connected_streaming_api:
            print("Warning: Streaming API seems connected already. Warranty void")
            return None

        # We've validated these two keys exists, no need to try-except
        account_id = self._auth_handshake['json']['currentAccountId']
        lightstream_endpoint = self._auth_handshake['json']['lightstreamerEndpoint']
        steaming_password = "CST-{}|XST-{}".format(self._auth_handshake['tokens']['CST'],
                                                   self._auth_handshake['tokens']['X-SECURITY-TOKEN'])
        streaming_url = "{}/lightstreamer/create_session.txt".format(lightstream_endpoint)

        print(f"Using account id\t\t\t{account_id}")
        print(f"Using endpoint\t\t\t\t{streaming_url}")

        # I haven't found any documentation regarding these parameters
        # It all is blind fate in https://labs.ig.com/node/557
        query = dict()
        query["LS_op2"] = "create"
        query["LS_cid"] = "mgQkwtwdysogQz2BJ4Ji kOj2Bg"
        query["LS_user"] = account_id
        query["LS_password"] = steaming_password

        rsp = self.__request_stream("POST", streaming_url, data=query, code=200)

        self.__validate_stream_rsp(rsp)

        self.connected_streaming_api = True
        print("--- Streaming api connected ---\n")

        return rsp

    def __validate_stream_rsp(self, rsp):
        """
        Validate stream response and save stream session variables.
        Note: Even though http ret code was 200, streaming endpoint might not be connected.
        :return:
        """

        # I haven't found any documentation regarding these variables (SessionId and ControlAdress)
        # It all is blind fate in https://labs.ig.com/node/557
        streaming_session = None
        control_domain = None
        streaming_iterator = rsp.iter_lines(chunk_size=80, decode_unicode=True)

        for line in streaming_iterator:
            if ":" not in line:
                continue
            [param, value] = line.split(":", 1)
            if param == "SessionId":
                streaming_session = value
            if param == "ControlAddress":
                control_domain = value
            if streaming_session and control_domain:
                break

        if not streaming_session or not control_domain:
            print("Error: could not find session and/or domain in streaming response")
            sys.exit(1)

        print(f"Found control address:\t\t\t{control_domain}")

        # Save variables
        self._auth_handshake['stream'] = dict()
        self._auth_handshake['stream']['session'] = streaming_session
        self._auth_handshake['stream']['control_domain'] = control_domain

    def log_out(self):
        """
        Log out of current session. Tokens will become invalid, reconnecting is necessary for future api calls
        :return:
        """

        print("--- Logging out ---")
        if not self.connected_rest_api:
            print("Warning: REST-API not connected")
        else:
            # Get url to connection endpoint
            #pkg = Login.base['DELETE']
            self.__request(Login.base, method='DELETE')
            print("Tokens now invalid")

        self._auth_handshake = None
        print("Flushed tokens")

        # Set flags
        self.connected_rest_api = False
        self.connected_streaming_api = False

        print("--- Logged out ---")

    def __get_rest_url(self, url_append):

        if self.account == 'demo':
            rest_url = self.url.protocol + "demo-" + self.url.base + url_append
        elif self.account == 'live':
            rest_url = self.url.protocol + self.url.base + url_append
        else:
            print(f"Error: account type not supported: {account}")
            sys.exit(1)

        return rest_url

    def __get_headers(self, version="1", tokens=False):
        headers = dict()
        headers['X-IG-API-KEY'] = self._api_key
        headers['Version'] = version
        headers['Content-Type'] = "application/json; charset=UTF-8"
        headers['Accept'] = "application/json; charset=UTF-8"

        if tokens:
            headers['CST'] = self._auth_handshake['tokens']['CST']
            headers['X-SECURITY-TOKEN'] = self._auth_handshake['tokens']['X-SECURITY-TOKEN']

        return headers

    def __validate_auth_response(self, rsp):
        """
        Check authentication response and extract necessary content
        :return:
        """
        print("Validating auth response")

        if rsp.status_code != 200:
            print(f"Error: failed to authenticate identity: {self._identity}: code: {rsp.status_code}")
            print(f"Error: {rsp.text}")
            sys.exit(1)

        print(f"Successfully authenticated:\t{self._identity}")
        print("Check auth tokens")

        # Check tokens
        auth_rsp = dict()
        auth_rsp['tokens'] = {}
        auth_rsp['json'] = None

        try:
            auth_rsp['tokens']['X-SECURITY-TOKEN'] = rsp.headers["X-SECURITY-TOKEN"]
            auth_rsp['tokens']['CST'] = rsp.headers["CST"]
        except AttributeError  as e:
            print("Error: failed extracting content from response")
            print(e)
            sys.exit(1)
        except KeyError as e:
            print("Error: key not found in response headers")
            print(e)
            sys.exit(1)

        print("...ok")

        print("Check auth variables")

        # Convert response to json (this will reformat response so fields like "headers" are lost)
        auth_rsp['json'] = rsp.json()

        # Check keys exist
        # Note: add keys to list if necessary later in API calls
        keys = ["currentAccountId", "lightstreamerEndpoint"]
        missing = False

        for key in keys:
            if key not in auth_rsp['json']:
                print(f"Error: missing key in response: {key}")
                missing = True

        if missing:
            print("Error: fatal error")
            sys.exit(1)

        print("...ok")

        return auth_rsp

    def __request(self, base=None, method=None, url_append='', body={}):

        if method not in base:
            print(f"Error: method not supported: {method}")
            sys.exit(1)

        pkg = base[method]
        url = self.__get_rest_url(base['path'] + url_append)
        headers = self.__get_headers(version=pkg['version'], tokens=pkg['tokens'])

        rsp = requests.request(method, url, headers=headers, json=body)

        if 'code' in pkg:
            exp_rsp_code = pkg['code']
        else:
            exp_rsp_code = 200

        if rsp.status_code != exp_rsp_code:
            print(f"Error: request failed with code: {rsp.status_code}:{rsp.text}")
            sys.exit(1)

        return rsp

    @staticmethod
    def __request_stream(method="", url="", data={}, code=-1):

        rsp = requests.request(method, url, data=data, stream=True)

        if rsp.status_code != code:
            print(f"Error: request failed with code: {rsp.status_code}:{rsp.text}")
            sys.exit(1)

        return rsp

