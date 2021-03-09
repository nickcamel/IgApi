from lib.ig_api import IgApi
import keyboard


if __name__ == "__main__":

    # Connect to demo account
    api = IgApi(account='demo')

    print("===== REST API DEMONSTRATION =====")

    # Get all watchlists AND specifically the id for watchlist "My Watchlist"
    watchlists, id = api.watchlists("My Watchlist")

    # Specifically get watchlist with id
    watchlist = api.watchlists_id(id)

    # Get the epic for the market "Sverige30 Cash (20SK)" in watchlist
    epic = api.get_market_epic_from_watchlist(watchlist, "Sverige30 Cash (20SK)")

    # Get prices for market with epic
    api.markets_prices_epic(epic)

    print("===== STREAMING API DEMONSTRATION =====")
    api.connect_streaming_api()

    # WIP: Need to add configurabiliy of subscription here.. 
    api.stream_subscribe(epic)

    # Print subscription
    try:
        for line in api.stream:
            if keyboard.is_pressed('q'):
                # Not optimal, but spam 'q' until detected
                break
            if "preamble" not in line.lower() and 'probe' not in line.lower():
                print("line", line)

    except Exception as e:
        # Don't kill the session, let's log out gracefully if possible
        print(e)
        pass

    # Log out (no further calls to api is accepted)
    api.log_out()
