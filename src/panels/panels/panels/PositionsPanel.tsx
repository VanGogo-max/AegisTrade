import React, { useEffect, useState } from "react"
import { useUIContexts } from "../ui/ui_contexts"
import { positionPanelTokens } from "../positions/position_panel_tokens"

interface Position {
  symbol: string
  pnl: number
  marginUsedPct: number
}

export const PositionsPanel: React.FC = () => {
  const { layoutState } = useUIContexts()
  const [positions, setPositions] = useState<Position[]>([])
  const collapsed = layoutState.collapsed["positions"]
  if (collapsed) return null

  useEffect(() => {
    const interval = setInterval(() => {
      setPositions([
        { symbol: "BTC/USDT", pnl: Math.random() * 200 - 100, marginUsedPct: Math.random() * 100 },
        { symbol: "ETH/USDT", pnl: Math.random() * 200 - 100, marginUsedPct: Math.random() * 100 }
      ])
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={{ background: positionPanelTokens.colors.backgroundColor, padding: 8, borderRadius: 4, minHeight: 150 }}>
      <h4 style={{ color: positionPanelTokens.colors.textColor }}>Open Positions</h4>
      {positions.map((pos) => (
        <div
          key={pos.symbol}
          style={{
            color:
              pos.pnl > 0
                ? positionPanelTokens.colors.profitColor
                : pos.pnl < 0
                ? positionPanelTokens.colors.lossColor
                : positionPanelTokens.colors.unrealizedColor,
            fontSize: positionPanelTokens.fontSizePx,
            background:
              pos.marginUsedPct > positionPanelTokens.riskThreshold
                ? positionPanelTokens.colors.riskHighlightColor
                : undefined,
            marginBottom: 2,
            padding: 2,
            borderRadius: 2
          }}
        >
          {pos.symbol}: {pos.pnl.toFixed(2)} USDT (Margin {pos.marginUsedPct.toFixed(0)}%)
        </div>
      ))}
    </div>
  )
}
