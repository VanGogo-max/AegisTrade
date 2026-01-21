import React, { useRef, useEffect, useState } from "react"
import { useUIContexts } from "../ui/ui_contexts"
import { createChart, IChartApi } from "lightweight-charts"
import { generateChartTheme } from "../chart/trading_chart_theme"
import { hyperliquidTheme } from "../theme/theme_tokens"

export const ChartPanel: React.FC = () => {
  const { layoutState } = useUIContexts()
  const chartContainer = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const [data, setData] = useState([{ time: "2026-01-21", open: 1000, high: 1010, low: 995, close: 1005 }])
  const collapsed = layoutState.collapsed["chart"]
  if (collapsed) return null

  useEffect(() => {
    if (!chartContainer.current) return
    const theme = generateChartTheme(hyperliquidTheme, true)
    const chart = createChart(chartContainer.current, {
      width: chartContainer.current.clientWidth,
      height: 300,
      layout: { background: { color: theme.backgroundColor }, textColor: theme.textColor },
      grid: { vertLines: { color: theme.gridColor }, horzLines: { color: theme.gridColor } },
      crosshair: { color: theme.crosshairColor },
      rightPriceScale: { borderColor: theme.axis.color },
      timeScale: { borderColor: theme.axis.color }
    })
    const candleSeries = chart.addCandlestickSeries({
      upColor: theme.candle.upColor,
      downColor: theme.candle.downColor,
      borderUpColor: theme.candle.upColor,
      borderDownColor: theme.candle.downColor,
      wickUpColor: theme.candle.wickColor,
      wickDownColor: theme.candle.wickColor
    })
    candleSeries.setData(data)
    chartRef.current = chart

    const interval = setInterval(() => {
      // Simulate new candle
      const last = data[data.length - 1]
      const next = {
        time: "2026-01-22",
        open: last.close,
        high: last.close + Math.random() * 5,
        low: last.close - Math.random() * 5,
        close: last.close + (Math.random() - 0.5) * 5
      }
      setData([...data, next])
      candleSeries.update(next)
    }, 5000)

    const handleResize = () => chart.applyOptions({ width: chartContainer.current!.clientWidth })
    window.addEventListener("resize", handleResize)
    return () => {
      clearInterval(interval)
      window.removeEventListener("resize", handleResize)
      chart.remove()
    }
  }, [data])

  return <div ref={chartContainer} style={{ borderRadius: 4 }} />
}
