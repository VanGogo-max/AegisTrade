FINAL
# Скрипт за автоматично изпълнение на поръчки от JSON (paper или real)
# Използва само твоите FINAL файлове:
# execution_engine, execution_scheduler, exchange_router,
# gmx_order_builder, gmx_real_signer, gmx_tx_sender, gmx_simulated_signer

import json
from execution_engine import ExecutionEngine
from execution_scheduler import ExecutionScheduler
from exchange_router import ExchangeRouter
from gmx_order_builder import GMXOrderBuilder
from gmx_real_signer import GMXRealSigner
from gmx_tx_sender import GMXTxSender
from gmx_simulated_signer import GMXSimulatedSigner

# ----------------------
# Настройка на режима
# "paper" -> симулация
# "real"  -> реална сделка
MODE = "paper"  # смени на "real" за реална транзакция

# Router и Order builder
router = ExchangeRouter()
order_builder = GMXOrderBuilder()

# Signer и TX sender според режима
if MODE == "paper":
    signer = GMXSimulatedSigner()
    tx_sender = None
else:
    signer = GMXRealSigner(private_key="0xYOUR_PRIVATE_KEY")
    tx_sender = GMXTxSender(rpc_url="https://YOUR_RPC_ENDPOINT")

# Execution engine и Scheduler
engine = ExecutionEngine(
    router=router,
    order_builder=order_builder,
    signer=signer,
    tx_sender=tx_sender,
    mode=MODE
)
scheduler = ExecutionScheduler(engine=engine)

# ----------------------
# Четене на поръчки от JSON файл
# JSON файлът трябва да съдържа списък от обекти като:
# [
#   {"symbol": "ETH-USD", "side": "long", "size_usd": 50, "leverage": 3, "order_type": "market"},
#   ...
# ]
JSON_FILE = "orders.json"

with open(JSON_FILE, "r") as f:
    orders = json.load(f)

# ----------------------
# Изпълнение на всички поръчки
results = []
for order_request in orders:
    result = scheduler.execute(order_request)
    results.append(result)
    print(f"Executed {order_request['symbol']} ({order_request['side']}): {result}")

# Резюме
print("\nAll results:")
for res in results:
    print(res)
