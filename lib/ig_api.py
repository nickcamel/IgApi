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
from positions import Positions
from client_sentiment import Sentiment


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
        self.stream = None

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

        url = epic
        custom = True
        if custom:
            get_res = ['?resolution=', 'SECOND']
            get_from = ['&from=', '2022-10-20T09:00:00']
            get_end = ['&to=', '2022-10-20T09:59:59']
            get_max = ['&max=', str(60*60)]
            #get_pagesize = ['&pageSize=', '0']
            url += "".join(get_res)
            url += "".join(get_from)
            url += "".join(get_end)
            url += "".join(get_max)
            #url += "".join(get_pagesize)
        #input(url)
        rsp = self.__request(Prices.epic, method='GET', url_append=url)

        rsp_json = rsp.json()
        pprint(rsp_json)

        return rsp_json

    def get_market_id_from_epic(self, epic):
        """
        Gets the id of a specific market using epic
        :param epic: (str) IG Market instrument
        :return: (json) prices
        """

        print("--- Get market id ---")
        print(f"Getting id of\t\t\t{epic}")

        url = epic
        rsp = self.__request(Prices.market_details, method='GET', url_append=url)

        rsp_json = rsp.json()

        try:
            return rsp_json['instrument']['marketId']
        except KeyError as e:
            print("Error: Market ID not found in response")
            print(rsp_json)
            print(e)
            sys.exit(1)
        except Exception as e:
            print("Error: unknown")
            print(e)
            sys.exit(1)

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

    def get_client_sentiment(self, id):
        print("--- Get Client Sentiment ---")
        print(f"id\t\t\t\t{id}")

        rsp = self.__request(Sentiment.base, method='GET', url_append=id)
        body = rsp.json()

        return body

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
            print("Warning: rest api seems connected already. Reconnecting...")

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
            print("Warning: Streaming API seems connected already. Reconnecting...")

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

    def stream_subscribe(self, epic):
        """
        WIP
        :param epic:
        :return:
        """
        control_url = "https://{}/lightstreamer/control.txt".format(self._auth_handshake['stream']['control_domain'])

        query = {}
        query["LS_session"] = self._auth_handshake['stream']['session']
        query["LS_op"] = "add"
        query["LS_table"] = "1"
        query["LS_id"] = f"MARKET:{epic}"  # "MARKET:IX.D.OMX.IFD.IP"
        query["LS_schema"] = "UPDATE_TIME BID OFFER"
        query["LS_mode"] = "MERGE"

        '''
        query = {}
        query["LS_session"] = self._auth_handshake['stream']['session']
        query["LS_op"] = "add"
        query["LS_table"] = "1"
        query["LS_id"] = f"CHART:{epic}:TICK"
        query["LS_schema"] = "UTM BID OFR"
        query["LS_mode"] = "DISTINCT"
        '''

        control_response = requests.request("POST", control_url, data=query)
        if control_response.status_code != 200:
            print("error", control_response.status_code, control_url, control_response.text)
            sys.exit(1)

    def positions(self, model, deal_id=''):
        if model == 'get' and not deal_id:
            print("Get all open deals")
            rsp = self.__request(Positions.base, method='GET')

            rsp_json = rsp.json()
            #pprint(rsp_json)

            return rsp_json
        elif model == 'get' and deal_id:
            print(f"Get open deal for {deal_id}")
            rsp = self.__request(Positions.base, method='GET', url_append=deal_id)
            rsp_json = rsp.json()
            pprint(rsp_json)

            return rsp_json

        else:
            print(f"Error: model not supported: {model}")

    def position_close(self, deal_id, direction, size_trade=1):
        print(f"Close deal for {deal_id}")
        body = dict()
        body["dealId"] = deal_id
        body["direction"] = direction
        body["epic"] = None
        body["expiry"] = None
        body["level"] = None
        body["orderType"] = 'MARKET'
        body['quoteId'] = None
        body["size"] = size_trade
        body['timeInForce'] = 'EXECUTE_AND_ELIMINATE'
        print(body)
        rsp = self.__request(Positions.trade, method='DELETE', body=body)
        rsp_json = rsp.json()
        print(f"Status: {rsp.status_code}")
        pprint(rsp_json)

        return rsp_json["dealReference"]

    def position_open(self, direction='', market='CS.D.ETHUSD.CFD.IP', size_trade=1, stop=40, limit=40):
        print(f"Open position")
        print(direction, market, size_trade, stop, limit)
        ref = direction
        if market == 'CS.D.ETHUSD.CFD.IP':
            currency = 'USD'
        else:
            currency = 'SEK'

        body = dict()
        body["dealReference"] = ref
        body["currencyCode"] = currency
        body["direction"] = direction
        body["epic"] = market
        body["expiry"] = '-'
        body["forceOpen"] = True
        body["guaranteedStop"] = False
        body["level"] = None
        body["limitDistance"] = limit
        body["limitLevel"] = None
        body["orderType"] = 'MARKET'
        body["size"] = size_trade
        body["stopDistance"] = stop
        body["stopLevel"] = None
        body["trailingStop"] = None
        body["trailingStopIncrement"] = None
        body["timeInForce"] = 'EXECUTE_AND_ELIMINATE'

        rsp = self.__request(Positions.trade, method='POST', body=body)
        #print(rsp)
        print(f"Status: {rsp.status_code}")

        rsp_json = rsp.json()
        pprint(rsp_json)

        return ref

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
        self.stream = streaming_iterator

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
            print(f"Error: account type not supported: {self.account}")
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
        print(url)
        headers = self.__get_headers(version=pkg['version'], tokens=pkg['tokens'])

        if base and base == Positions.trade and method == 'DELETE':
            # https://labs.ig.com/node/36
            # print("CHANGING HEADERS")
            method = 'POST'
            headers['_method'] = 'DELETE'

        # print(method)
        # print(url)
        # print(headers)

        if body:
            rsp = requests.request(method, url, headers=headers, json=body)
        else:
            rsp = requests.request(method, url, headers=headers)
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

        rsp = requests.request(method, url, data=data, stream=True, timeout=15)

        if rsp.status_code != code:
            print(f"Error: request failed with code: {rsp.status_code}:{rsp.text}")
            sys.exit(1)

        return rsp

