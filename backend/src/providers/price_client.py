class PriceClient:
    """Placeholder for optional free price providers.

    The MVP keeps share price as a manual input so the model does not depend on
    unofficial market-data APIs.
    """

    def latest_price(self, ticker: str) -> float | None:
        return None
