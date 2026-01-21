import { useEffect, useRef, useState } from "react"

interface WebSocketData {
  orderbook?: any
  trades?: any[]
  positions?: any[]
  orders?: any[]
  balances?: any[]
  chart?: any[]
}

export const useWebSocket = (url: string) => {
  const wsRef = useRef<WebSocket | null>(null)
  const [data, setData] = useState<WebSocketData>({
    orderbook: {},
    trades: [],
    positions: [],
    orders: [],
    balances: [],
    chart: []
  })

  useEffect(() => {
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data)

      setData((prev) => ({
        ...prev,
        orderbook: msg.orderbook || prev.orderbook,
        trades: msg.trades || prev.trades,
        positions: msg.positions || prev.positions,
        orders: msg.orders || prev.orders,
        balances: msg.balances || prev.balances,
        chart: msg.chart || prev.chart
      }))
    }

    ws.onclose = () => console.log("WebSocket closed")
    ws.onerror = (err) => console.error("WebSocket error:", err)

    return () => ws.close()
  }, [url])

  return data
}
