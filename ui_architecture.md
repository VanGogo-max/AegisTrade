# Web UI Architecture – DEX Trading Platform

## 1. Goals

- Професионален DeFi трейдинг интерфейс
- Тъмен стил, вдъхновен от Hyperliquid
- Поддръжка на 10 езика (i18n, включително RTL за العربية)
- Реално време: позиции, риск, PnL, стратегии, абонамент
- Свързан директно с Core Engine и Subscription Manager

---

## 2. Technology Stack

- Framework: Next.js (React, TypeScript)
- Styling: Tailwind CSS (custom dark theme)
- Charts: TradingView Lightweight Charts / Recharts
- State: Zustand
- i18n: i18next + JSON dictionaries
- API: REST / WebSocket към Core Engine
- Theme: Dark DeFi (неонови акценти, low-noise)

---

## 3. Layout Structure

