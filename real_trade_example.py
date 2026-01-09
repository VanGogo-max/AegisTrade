from execution_engine import ExecutionEngine
from execution_scheduler import ExecutionScheduler
from exchange_router import ExchangeRouter
from gmx_order_builder import GMXOrderBuilder
from gmx_real_signer import GMXRealSigner
from gmx_tx_sender import GMXTxSender

# Router
router = ExchangeRouter()

# Order builder
order_builder = GMXOrderBuilder()

# Real signer
signer = GMXRealSigner(private_key="0xYOUR_PRIVATE_KEY")

# TX sender
tx_sender = GMXTxSender(rpc_url="https://YOUR_RPC_ENDPOINT")

# Engine
engine = ExecutionEngine(
    router=router,
    order_builder=order_builder,
    signer=signer,
    tx_sender=tx_sender,
    mode="real"
)

# Scheduler
scheduler = ExecutionScheduler(engine=engine)

# Order
order_request = {
    "symbol": "ETH-USD",
    "side": "long",
    "size_usd": 50,
    "leverage": 3,
    "order_type": "market"
}

# Execute
tx_result = scheduler.execute(order_request)
print(tx_result)
