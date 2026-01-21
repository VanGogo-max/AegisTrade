// src/orderbook/orderbook_tokens.ts

export interface OrderbookColors {
  bidColor: string
  askColor: string
  bidDepthGradient: string
  askDepthGradient: string
  highlightColor: string
  textColor: string
  backgroundColor: string
}

export interface OrderbookAnimation {
  fadeDurationMs: number
  slideDurationMs: number
  maxOpacity: number
}

export interface OrderbookTokens {
  colors: OrderbookColors
  animation: OrderbookAnimation
  rowHeightPx: number
  fontSizePx: number
  maxVisibleOrders: number
  depthHighlightThreshold: number // % change to trigger highlight
}

export const orderbookTokens: OrderbookTokens = {
  colors: {
    bidColor: "#22C55E", // green
    askColor: "#EF4444", // red
    bidDepthGradient: "linear-gradient(to right, #22C55E33, #22C55E88)",
    askDepthGradient: "linear-gradient(to right, #EF444433, #EF444488)",
    highlightColor: "#FACC15", // yellow for recent fills
    textColor: "#F9FAFB", // light gray
    backgroundColor: "#1F2937" // dark background
  },
  animation: {
    fadeDurationMs: 300,
    slideDurationMs: 150,
    maxOpacity: 0.8
  },
  rowHeightPx: 24,
  fontSizePx: 12,
  maxVisibleOrders: 20,
  depthHighlightThreshold: 0.2 // highlight if price change > 0.2%
}
