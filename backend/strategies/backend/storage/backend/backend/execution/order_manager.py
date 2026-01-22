import asyncio
from typing import Dict, Any, Callable, List
from enum import Enum

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"

class Order:
    def __init__(self, symbol: str, side: OrderSide, qty: float, price: float | None = None, type_: OrderType = OrderType.MARKET, exchange: str = "binance"):
        self.symbol = symbol
        self.side = side
        self.qty = qty
        self.price = price
        self.type = type_
        self.exchange = exchange
        self.status = "pending"  # pending, filled, failed
        self.response = None

class OrderManager:
    def __init__(self, risk_check: Callable[[Order], bool], send_order_callable: Callable[[Order], Any]):
        """
        risk_check: callable(Order) -> bool, True ако може да се изпълни
        send_order_callable: callable(Order) -> async отправка към exchange
        """
        self.risk_check = risk_check
        self.send_order = send_order_callable
        self.queue: asyncio.Queue = asyncio.Queue()
        self.running = False

    # ===== Signal Ingress =====
    async def submit_order(self, order: Order):
        await self.queue.put(order)

    # ===== Core Loop =====
    async def start(self):
        self.running = True
        while self.running:
            order: Order = await self.queue.get()
            await self.execute_order(order)

    # ===== Order Execution =====
    async def execute_order(self, order: Order):
        # Risk check
        if not self.risk_check(order):
            order.status = "rejected"
            print(f"[OrderManager] Order rejected by risk: {order.symbol} {order.side} {order.qty}")
            return

        # Attempt execution
        try:
            response = await self.send_order(order)
            order.status = "filled"
            order.response = response
            print(f"[OrderManager] Order filled: {order.symbol} {order.side} {order.qty} @ {order.price}")
        except Exception as e:
            order.status = "failed"
            order.response = str(e)
            print(f"[OrderManager] Order failed: {order.symbol} {order.side} {order.qty}, error: {e}")

# ========== Example Risk Check ==========
def simple_risk_check(order: Order) -> bool:
    # Пример: reject ако qty <= 0
    return order.qty > 0

# ========== Example Send Order (stub) ==========
async def mock_send_order(order: Order):
    await asyncio.sleep(0.05)  # симулира време за API call
    return {"orderId": 12345, "status": "filled"}

# ========== Bootstrap Example ==========
async def bootstrap_order_manager():
    manager = OrderManager(risk_check=simple_risk_check, send_order_callable=mock_send_order)
    asyncio.create_task(manager.start())
    return manager
