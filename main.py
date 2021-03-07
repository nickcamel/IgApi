from lib.ig_api import IgApi


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
    # This section is WIP
    api.connect_streaming_api()

    # api.stream_subscribe(epic)  # TODO: Develop

    # Log out (no further calls to api is accepted)
    api.log_out()
