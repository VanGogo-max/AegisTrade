FINAL
# Скрипт за минимално paper → real trading с GMX
# Използва само твоите FINAL файлове:
# execution_engine, execution_scheduler, exchange_router,
# gmx_order_builder, gmx_real_signer, gmx_tx_sender, gmx_simulated_signer

from execution_engine import ExecutionEngine
from execution_scheduler import ExecutionScheduler
from exchange_router import ExchangeRouter
from gmx_order_builder import GMXOrderBuilder
from gmx_real_signer import GMXRealSigner
from gmx_tx_sender import GMXTxSender
from gmx_simulated_signer import GMXSimulatedSigner

# Настройка на режима
# "paper" -> симулация
# "real"  -> реална сделка
MODE = "paper"  # смени на "real" за реална транзакция

# Router
router = ExchangeRouter()

# Order builder
order_builder = GMXOrderBuilder()

# Signer и TX sender според режима
if MODE == "paper":
    signer = GMXSimulatedSigner()
    tx_sender = None
else:
    signer = GMXRealSigner(private_key="0xYOUR_PRIVATE_KEY")
    tx_sender = GMXTxSender(rpc_url="https://YOUR_RPC_ENDPOINT")

# Execution engine
engine = ExecutionEngine(
    router=router,
    order_builder=order_builder,
    signer=signer,
    tx_sender=tx_sender,
    mode=MODE
)

# Scheduler
scheduler = ExecutionScheduler(engine=engine)

# Примерна поръчка
order_request = {
    "symbol": "ETH-USD",
    "side": "long",
    "size_usd": 50,
    "leverage": 3,
    "order_type": "market"
}

# Изпълнение
result = scheduler.execute(order_request)
print(result)
