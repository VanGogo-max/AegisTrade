// src/chart/trading_chart_theme.ts

import { ThemeTokens } from "../theme/theme_tokens"

export interface TradingChartTheme {
  backgroundColor: string
  textColor: string
  gridColor: string
  crosshairColor: string
  candle: {
    upColor: string
    downColor: string
    borderVisible: boolean
    wickColor: string
  }
  lineSeries: {
    color: string
    lineWidth: number
  }
  overlay: {
    buyZoneColor: string
    sellZoneColor: string
    alpha: number
  }
  axis: {
    fontFamily: string
    fontSize: number
    color: string
  }
}

export const generateChartTheme = (theme: ThemeTokens, darkMode: boolean = true): TradingChartTheme => {
  const bg = darkMode ? theme.colors.background[900] : theme.colors.background[50]
  const text = darkMode ? theme.colors.text[50] : theme.colors.text[900]
  const grid = darkMode ? theme.colors.gray[700] : theme.colors.gray[300]
  const crosshair = darkMode ? theme.colors.blue[400] : theme.colors.blue[600]

  return {
    backgroundColor: bg,
    textColor: text,
    gridColor: grid,
    crosshairColor: crosshair,
    candle: {
      upColor: theme.colors.green[400],
      downColor: theme.colors.red[400],
      borderVisible: true,
      wickColor: darkMode ? theme.colors.gray[300] : theme.colors.gray[700]
    },
    lineSeries: {
      color: theme.colors.purple[400],
      lineWidth: 2
    },
    overlay: {
      buyZoneColor: theme.colors.green[300],
      sellZoneColor: theme.colors.red[300],
      alpha: 0.2
    },
    axis: {
      fontFamily: theme.typography.fontFamily,
      fontSize: 12,
      color: text
    }
  }
}
