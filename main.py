from lib.ig_api import IgApi
import keyboard


if __name__ == "__main__":

    # Connect to demo account
    api = IgApi(account='demo')
    from pprint import pprint
    #pprint(api._auth_handshake)
    print("===== REST API DEMONSTRATION =====")

    get_epic_from_watchlist = False

    if get_epic_from_watchlist:
        # Get all watchlists AND specifically the id for watchlist "My Watchlist"
        watchlists, id = api.watchlists("My Watchlist")

        # Specifically get watchlist with id
        watchlist = api.watchlists_id(id)

        pprint(watchlists)

        # Get the epic for the market "Sverige30 Cash (20SK)" in watchlist
        epic = api.get_market_epic_from_watchlist(watchlist, "Sverige30 Cash (20SK)")

        print("EPIC ===>", epic)
        # Get prices for market with epic
        api.markets_prices_epic(epic)
    else:
        epic = 'IX.D.OMX.IFM.IP'  # OMXS30

    print("CLIENT SENTIMENT ===>", epic)
    market_id = api.get_market_id_from_epic(epic)
    print(f"Got market id: {market_id}")

    rsp = api.get_client_sentiment(market_id)

    long = rsp['longPositionPercentage']
    short = rsp['shortPositionPercentage']
    print(f"long: {long}\nshort: {short}")

    input()
    print("===== STREAMING API DEMONSTRATION =====")
    api.connect_streaming_api()

    # WIP: Need to add configurabiliy of subscription here..
    #api.stream_subscribe(epic)
    k_positions = 0
    while k_positions < 1:
        k_positions += 1

        import time
        input("----> Continue to open position? <----")
        ref = api.position_open('BUY', market='IX.D.OMX.IFM.IP')

        deal_id = ""
        while not deal_id:
            rsp = api.positions('get')
            if rsp and 'positions' in rsp and len(rsp['positions']) > 0:
                for deals in rsp['positions']:
                    if rsp and deals['position']['dealReference'] == ref:
                        deal_id = deals['position']['dealId']
                    else:
                        print("Not opened yet")
                        time.sleep(1)
            else:
                print("No deals found")
                time.sleep(1)

        input("OPENED.. CHECK IT")
        deal_id = []
        direction = []
        for deals in rsp['positions']:
            print(deals)
            deal_id.append(deals['position']['dealId'])
            direction.append(deals['position']['direction'])

        print(deal_id)
        input("waiting")
        for k, deal in enumerate(deal_id):
            rsp = api.positions('get', deal)
            input(rsp)
            position = {}
            position['bid'] = rsp['market']['bid']
            position['offer'] = rsp['market']['offer']
            position['direction'] = rsp['position']['direction']
            position['price'] = rsp['position']['level']
            position['limit'] = rsp['position']['limitLevel']
            position['stop'] = rsp['position']['stopLevel']

            from pprint import pprint
            #pprint(position)

            if direction[k] == 'BUY':
                dir_close = 'SELL'
            elif direction[k] == 'SELL':
                dir_close = 'BUY'

            api.position_close(deal, dir_close)



        """
        # Print streamed data
        due_key = False
        try:
            while True:
                try:
                    api.stream_subscribe(epic)
                except StopIteration:
                    print("Error: Stream pipe lost. Consider reconnecting")
                    due_key = True
                    break
    
                for line in api.stream:
                    if keyboard.is_pressed('q'):
                        # Not optimal, but spam 'q' until detected
                        print("Quit")
                        due_key = True
                        break
    
                    if "preamble" not in line.lower() and 'probe' not in line.lower():
                        import datetime
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"{now}--> line: {line}")
    
                if due_key:
                    break
    
        except Exception as e:
            # Don't kill the session, let's log out gracefully if possible
            print(e)
            pass
        """

    # Log out (no further calls to api is accepted)
    api.log_out()
