import asyncio
from web3 import Web3
from typing import Callable, Dict, List

from backend.exchange_connectors.base import BaseExchangeConnector


class GMXWeb3Connector(BaseExchangeConnector):
    """
    GMX connector via Web3 on-chain events
    """
    def __init__(
        self,
        symbols: List[str],
        on_message: Callable[[Dict], None],
        rpc_url: str = "https://arb1.arbitrum.io/rpc"
    ):
        super().__init__("gmx", symbols, on_message)
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.running = False

        # TODO: сложи реалните адреси и ABI на GMX контракти
        self.position_manager_address = "0xYourGMXPositionManager"
        self.position_manager_abi = []  # JSON ABI list

    async def start(self):
        self.running = True
        contract = self.w3.eth.contract(
            address=self.position_manager_address,
            abi=self.position_manager_abi
        )

        event_filter = contract.events.UpdatePosition.createFilter(fromBlock='latest')

        while self.running:
            try:
                for event in event_filter.get_new_entries():
                    symbol = event['args']['symbol']
                    if symbol not in self.symbols:
                        continue
                    data = {
                        "exchange": self.name,
                        "symbol": symbol,
                        "type": "trade",
                        "timestamp": event['args']['timestamp'],
                        "data": {
                            "price": float(event['args']['price']),
                            "qty": float(event['args']['size']),
                            "side": "buy" if event['args']['isLong'] else "sell",
                        }
                    }
                    await self.on_message(data)
            except Exception as e:
                print(f"[GMX] Error: {e}, reconnecting in 5s")
                await asyncio.sleep(5)

    async def connect(self):
        await self.start()

    async def disconnect(self):
        self.running = False
