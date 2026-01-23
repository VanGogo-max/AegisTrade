import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from backend.exchange_connectors.apex_ws import ApexWSConnector
from backend.exchange_connectors.dydx_ws import DydxWSConnector
from backend.exchange_connectors/gmx_subgraph import GMXSubgraphConnector
from backend.exchange_connectors.hyperliquid_ws import HyperliquidWSConnector
from backend.exchange_connectors.kcex_stub import KCEXStubConnector
from backend.exchange_connectors.kwenta_ws import KwentaWSConnector
from backend.exchange_connectors.vertex_ws import VertexWSConnector

from backend.market_router import UnifiedMarketDataRouter
from backend.strategy_engine import StrategyEngine
from backend.timeseries_recorder import TimeseriesRecorder

app = FastAPI(title="Multi-DEX Trading Platform")

# CORS ако е необходимо
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket клиенти
ws_clients = {}

# Lifespan startup/shutdown
@app.on_event("startup")
async def startup_event():
    global market_router
    loop = asyncio.get_event_loop()

    # Инициализация на connectors
    connectors = [
        ApexWSConnector(loop),
        DydxWSConnector(loop),
        GMXSubgraphConnector(loop),
        HyperliquidWSConnector(loop),
        KCEXStubConnector(loop),  # stub – по-късно заменяме с реален API
        KwentaWSConnector(loop),
        VertexWSConnector(loop),
    ]

    # Unified router за всички connectors
    market_router = UnifiedMarketDataRouter(connectors)
    await market_router.start_all()  # стартира слушането на всички потоци

    # Инициализация на Strategy Engine
    app.state.strategy_engine = StrategyEngine(market_router)
    app.state.recorder = TimeseriesRecorder(market_router)
    loop.create_task(app.state.strategy_engine.run())
    loop.create_task(app.state.recorder.run())

@app.on_event("shutdown")
async def shutdown_event():
    await market_router.stop_all()

# HTTP endpoint за health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# WebSocket endpoint за реално време market data
@app.websocket("/ws/market/{client_id}")
async def ws_market(client_id: str, websocket: WebSocket):
    await websocket.accept()
    ws_clients[client_id] = websocket

    async def send_event(event):
        try:
            await websocket.send_json(event)
        except Exception:
            pass

    # Абониране за всички connectors
    for connector in market_router.connectors:
        connector.register_handler("trade", send_event)
        connector.register_handler("position", send_event)

    try:
        while True:
            msg = await websocket.receive_text()
            # Може да се добави обработка на входни заявки (subscribe/unsubscribe)
    except Exception:
        pass
    finally:
        ws_clients.pop(client_id, None)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
