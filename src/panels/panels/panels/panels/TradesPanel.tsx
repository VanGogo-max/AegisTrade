import React, { useEffect, useState } from "react"
import { useUIContexts } from "../ui/ui_contexts"

interface Trade {
  time: string
  symbol: string
  side: "buy" | "sell"
  price: number
  size: number
}

export const TradesPanel: React.FC = () => {
  const { layoutState } = useUIContexts()
  const [trades, setTrades] = useState<Trade[]>([])
  const collapsed = layoutState.collapsed["trades"]
  if (collapsed) return null

  useEffect(() => {
    const interval = setInterval(() => {
      setTrades((prev) => [
        ...prev.slice(-9), // keep last 10
        {
          time: new Date().toLocaleTimeString(),
          symbol: "BTC/USDT",
          side: Math.random() > 0.5 ? "buy" : "sell",
          price: 1000 + Math.random() * 20,
          size: Math.random() * 5
        }
      ])
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={{ background: "#0D1117", padding: 8, borderRadius: 4, minHeight: 150 }}>
      <h4 style={{ color: "#FFF" }}>Recent Trades</h4>
      {trades.map((t, i) => (
        <div key={i} style={{ color: t.side === "buy" ? "#4CAF50" : "#F44336", fontSize: 12 }}>
          {t.time} {t.symbol} {t.side.toUpperCase()} {t.size.toFixed(2)} @ {t.price.toFixed(2)}
        </div>
      ))}
    </div>
  )
}
