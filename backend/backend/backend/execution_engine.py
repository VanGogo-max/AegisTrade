# ================================
# execution_engine.py (PRO)
# ================================

import asyncio
import random


class ExecutionEngine:
    def __init__(self, clients):
        """
        clients = {
            "binance": client_object,
            "bybit": client_object
        }
        """
        self.clients = clients

        # настройки
        self.max_retries = 3
        self.slippage_tolerance = 0.002  # 0.2%

    # =========================
    # GET BEST CLIENT
    # =========================
    def _select_client(self, symbol):
        # можеш да добавиш routing логика
        return list(self.clients.values())[0]

    # =========================
    # SIMULATED PRICE FETCH
    # =========================
    async def _get_market_price(self, client, symbol):
        ticker = await client.fetch_ticker(symbol)
        return ticker["last"]

    # =========================
    # EXECUTE ORDER
    # =========================
    async def execute_order(self, signal):
        symbol = signal["symbol"]
        side = signal["side"]
        size = signal["size"]

        client = self._select_client(symbol)

        for attempt in range(self.max_retries):

            try:
                market_price = await self._get_market_price(client, symbol)

                # =========================
                # LIMIT PRICE WITH SLIPPAGE CONTROL
                # =========================
                if side == "buy":
                    limit_price = market_price * (1 + self.slippage_tolerance)
                else:
                    limit_price = market_price * (1 - self.slippage_tolerance)

                # =========================
                # PLACE LIMIT ORDER
                # =========================
                order = await client.create_order(
                    symbol=symbol,
                    type="limit",
                    side=side,
                    amount=size,
                    price=limit_price
                )

                # =========================
                # WAIT FOR FILL
                # =========================
                filled_order = await self._wait_for_fill(client, order["id"], symbol)

                if filled_order:
                    return {
                        "id": order["id"],
                        "price": filled_order["average"],
                        "filled": filled_order["filled"]
                    }

                # =========================
                # FALLBACK TO MARKET
                # =========================
                print(f"[FALLBACK MARKET] {symbol}")

                market_order = await client.create_order(
                    symbol=symbol,
                    type="market",
                    side=side,
                    amount=size
                )

                return {
                    "id": market_order["id"],
                    "price": market_order["average"],
                    "filled": market_order["filled"]
                }

            except Exception as e:
                print(f"[EXEC RETRY {attempt}] {symbol}: {e}")
                await asyncio.sleep(1)

        raise Exception(f"Execution failed for {symbol}")

    # =========================
    # WAIT FOR FILL
    # =========================
    async def _wait_for_fill(self, client, order_id, symbol):
        for _ in range(5):
            order = await client.fetch_order(order_id, symbol)

            if order["status"] == "closed":
                return order

            await asyncio.sleep(1)

        return None

    # =========================
    # CLOSE POSITION
    # =========================
    async def close_position(self, symbol):
        client = self._select_client(symbol)

        # NOTE: тук трябва да знаеш size + side
        # за demo ще затворим с market

        ticker = await client.fetch_ticker(symbol)
        price = ticker["last"]

        side = "sell"  # или buy ако е short (трябва да го подадеш)

        order = await client.create_order(
            symbol=symbol,
            type="market",
            side=side,
            amount=0.01  # трябва да е реалният size!
        )

        return {
            "id": order["id"],
            "price": price
        }
