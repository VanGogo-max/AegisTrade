// src/positions/position_panel_tokens.ts

export interface PositionColors {
  profitColor: string
  lossColor: string
  unrealizedColor: string
  leverageColor: string
  backgroundColor: string
  borderColor: string
  textColor: string
  riskHighlightColor: string
}

export interface PositionPanelTokens {
  colors: PositionColors
  rowHeightPx: number
  fontSizePx: number
  maxVisiblePositions: number
  pnlGradientSteps: number
  riskThreshold: number // % of margin considered high risk
  highlightFadeMs: number
}

export const positionPanelTokens: PositionPanelTokens = {
  colors: {
    profitColor: "#22C55E",       // green
    lossColor: "#EF4444",         // red
    unrealizedColor: "#FBBF24",   // yellow/orange
    leverageColor: "#3B82F6",     // blue
    backgroundColor: "#111827",   // dark background
    borderColor: "#374151",       // gray border
    textColor: "#F9FAFB",         // light text
    riskHighlightColor: "#F87171" // intense red for high risk
  },
  rowHeightPx: 28,
  fontSizePx: 13,
  maxVisiblePositions: 15,
  pnlGradientSteps: 5,
  riskThreshold: 50, // highlight if margin usage >50%
  highlightFadeMs: 400
}
