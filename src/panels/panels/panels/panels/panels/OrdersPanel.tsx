import React, { useEffect, useState } from "react"
import { useUIContexts } from "../ui/ui_contexts"

interface Order {
  id: string
  symbol: string
  side: "buy" | "sell"
  price: number
  size: number
  status: "open" | "filled" | "canceled"
}

export const OrdersPanel: React.FC = () => {
  const { layoutState } = useUIContexts()
  const [orders, setOrders] = useState<Order[]>([])
  const collapsed = layoutState.collapsed["orders"]
  if (collapsed) return null

  useEffect(() => {
    const interval = setInterval(() => {
      setOrders([
        { id: "1", symbol: "BTC/USDT", side: "buy", price: 1005, size: 1, status: "open" },
        { id: "2", symbol: "ETH/USDT", side: "sell", price: 1010, size: 0.5, status: "filled" }
      ])
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={{ background: "#0D1117", padding: 8, borderRadius: 4, minHeight: 150 }}>
      <h4 style={{ color: "#FFF" }}>Your Orders</h4>
      {orders.map((o) => (
        <div
          key={o.id}
          style={{ color: o.status === "open" ? "#2196F3" : o.status === "filled" ? "#4CAF50" : "#F44336", fontSize: 12 }}
        >
          {o.symbol} {o.side.toUpperCase()} {o.size} @ {o.price} ({o.status})
        </div>
      ))}
    </div>
  )
}
