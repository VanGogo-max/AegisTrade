async def get_price(self, symbol: str):
    """
    GMX няма direct spot price API → използваме reader/vault approximation
    """

    WETH = Web3.to_checksum_address(
        "0x82af49447d8a07e3bd95bd0d56f35241523fbab1"
    )

    collateral_tokens = [WETH]
    index_tokens = [WETH]
    is_long = [True]

    result = self.reader.functions.getPositions(
        self.vault_address,
        self.account,
        collateral_tokens,
        index_tokens,
        is_long
    ).call()

    # fallback price (GMX не дава чист market price тук)
    if not result or len(result) < 3:
        return 3000

    entry_price = result[2] / 1e30

    return entry_price
