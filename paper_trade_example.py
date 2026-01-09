from execution_engine import ExecutionEngine
from execution_scheduler import ExecutionScheduler
from exchange_router import ExchangeRouter
from gmx_order_builder import GMXOrderBuilder
from gmx_simulated_signer import GMXSimulatedSigner

# Router
router = ExchangeRouter()

# Order builder
order_builder = GMXOrderBuilder()

# Paper signer
signer = GMXSimulatedSigner()

# Engine
engine = ExecutionEngine(
    router=router,
    order_builder=order_builder,
    signer=signer,
    tx_sender=None,  # paper mode
    mode="paper"
)

# Scheduler
scheduler = ExecutionScheduler(engine=engine)

# Order
order_request = {
    "symbol": "ETH-USD",
    "side": "long",
    "size_usd": 100,
    "leverage": 5,
    "order_type": "market"
}

# Execute
result = scheduler.execute(order_request)
print(result)
