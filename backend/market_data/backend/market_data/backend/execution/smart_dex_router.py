import os
from typing import Dict, Any, List

from backend.market_data.liquidity_analyzer import LiquidityAnalyzer
from backend.market_data.funding_analyzer import FundingAnalyzer


class SmartDexRouter:

    def __init__(self, dex_clients: Dict[str, Any]):

        self.dex_clients = dex_clients

        self.liquidity_analyzer = LiquidityAnalyzer()
        self.funding_analyzer = FundingAnalyzer()

        self.liquidity_weight = float(os.getenv("LIQUIDITY_WEIGHT", 0.6))
        self.funding_weight = float(os.getenv("FUNDING_WEIGHT", 0.4))

        self.split_threshold = float(os.getenv("SPLIT_THRESHOLD", 10000))

    async def evaluate_dex(
        self,
        dex_name: str,
        symbol: str,
        side: str,
        size: float,
    ) -> Dict:

        client = self.dex_clients[dex_name]

        orderbook = await client.get_orderbook(symbol)
        funding_rate = await client.get_funding_rate(symbol)

        liquidity_data = self.liquidity_analyzer.analyze(
            orderbook,
            "buy" if side.lower() == "long" else "sell",
            size,
        )

        if not liquidity_data["valid"]:
            return {"valid": False}

        funding_data = self.funding_analyzer.analyze(
            funding_rate,
            size,
            side,
        )

        final_score = (
            self.liquidity_weight * liquidity_data["liquidity_score"]
            + self.funding_weight * funding_data["funding_score"]
        )

        return {
            "valid": True,
            "dex": dex_name,
            "final_score": final_score,
            "liquidity": liquidity_data,
            "funding": funding_data,
        }

    async def route_order(
        self,
        symbol: str,
        side: str,
        size: float,
        leverage: int,
    ):

        evaluations: List[Dict] = []

        for dex in self.dex_clients.keys():
            result = await self.evaluate_dex(dex, symbol, side, size)
            if result["valid"]:
                evaluations.append(result)

        if not evaluations:
            raise Exception("No valid DEX available")

        # Sort by score descending
        evaluations.sort(key=lambda x: x["final_score"], reverse=True)

        # SPLIT LOGIC
        if size >= self.split_threshold and len(evaluations) > 1:
            return await self.split_execute(
                evaluations,
                symbol,
                side,
                size,
                leverage,
            )

        # Single best DEX
        best = evaluations[0]
        client = self.dex_clients[best["dex"]]

        return await client.place_order(
            symbol=symbol,
            side=side,
            size=size,
            leverage=leverage,
        )

    async def split_execute(
        self,
        evaluations: List[Dict],
        symbol: str,
        side: str,
        size: float,
        leverage: int,
    ):

        total_score = sum(e["final_score"] for e in evaluations[:3])

        results = []

        for e in evaluations[:3]:

            weight = e["final_score"] / total_score
            allocated_size = size * weight

            client = self.dex_clients[e["dex"]]

            result = await client.place_order(
                symbol=symbol,
                side=side,
                size=allocated_size,
                leverage=leverage,
            )

            results.append(result)

        return results
