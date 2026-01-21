import React, { useEffect, useState } from "react"
import { useUIContexts } from "../ui/ui_contexts"

interface Balance {
  asset: string
  available: number
  locked: number
}

export const BalancesPanel: React.FC = () => {
  const { layoutState } = useUIContexts()
  const [balances, setBalances] = useState<Balance[]>([])
  const collapsed = layoutState.collapsed["balances"]
  if (collapsed) return null

  useEffect(() => {
    const interval = setInterval(() => {
      setBalances([
        { asset: "USDT", available: 500, locked: 50 },
        { asset: "BTC", available: 0.5, locked: 0.1 },
        { asset: "ETH", available: 1.2, locked: 0.3 }
      ])
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={{ background: "#0D1117", padding: 8, borderRadius: 4, minHeight: 150 }}>
      <h4 style={{ color: "#FFF" }}>Balances</h4>
      {balances.map((b) => (
        <div key={b.asset} style={{ fontSize: 12, color: "#FFF" }}>
          {b.asset}: Available {b.available} | Locked {b.locked}
        </div>
      ))}
    </div>
  )
}
