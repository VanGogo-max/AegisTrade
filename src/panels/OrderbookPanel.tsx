import React, { useEffect, useState } from "react"
import { useUIContexts } from "../ui/ui_contexts"
import { orderbookTokens } from "../orderbook/orderbook_tokens"

interface Order {
  price: number
  size: number
}

export const OrderbookPanel: React.FC = () => {
  const { layoutState } = useUIContexts()
  const [bids, setBids] = useState<Order[]>([])
  const [asks, setAsks] = useState<Order[]>([])
  const collapsed = layoutState.collapsed["orderbook"]
  if (collapsed) return null

  // Example: simulate live WebSocket updates
  useEffect(() => {
    const interval = setInterval(() => {
      setBids([{ price: 1000 + Math.random() * 5, size: Math.random() * 10 }])
      setAsks([{ price: 1005 + Math.random() * 5, size: Math.random() * 10 }])
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={{ background: orderbookTokens.colors.backgroundColor, padding: 8, borderRadius: 4, minHeight: 200 }}>
      <h4 style={{ color: orderbookTokens.colors.textColor }}>Orderbook</h4>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: orderbookTokens.fontSizePx }}>
        <div style={{ color: orderbookTokens.colors.bidColor }}>
          Bids: {bids.map((b) => `${b.price.toFixed(1)} (${b.size.toFixed(1)})`).join(", ")}
        </div>
        <div style={{ color: orderbookTokens.colors.askColor }}>
          Asks: {asks.map((a) => `${a.price.toFixed(1)} (${a.size.toFixed(1)})`).join(", ")}
        </div>
      </div>
    </div>
  )
}
