# Theme Tokens – Hyperliquid Style (Dark DeFi UI)

## 1. Design Goals

- Визуално усещане като Hyperliquid
- Тъмен, контрастен, „чист“ трейдинг интерфейс
- Минимален шум, фокус върху графики и числа
- Неонови акценти за важни състояния (PnL, риск, статус)

---

## 2. Core Colors

### Backgrounds
- App Background: `#0B0E14`
- Panel Background: `#121826`
- Card Background: `#161D2A`
- Modal Background: `#0F1420`

### Borders & Dividers
- Border Default: `#1E293B`
- Border Active: `#2DD4BF`
- Grid Lines: `#1A2234`

---

## 3. Text Colors

- Primary Text: `#E5E7EB`
- Secondary Text: `#9CA3AF`
- Muted Text: `#6B7280`
- Disabled Text: `#4B5563`

---

## 4. Trading Colors

### PnL
- Profit Green: `#00FFA3`
- Loss Red: `#FF4D4D`
- Neutral Gray: `#A1A1AA`

### Risk / Warning
- Warning Yellow: `#FACC15`
- Danger Orange: `#FB7185`

### Accents
- Neon Cyan: `#22D3EE`
- Neon Purple: `#A78BFA`
- Electric Blue: `#3B82F6`

---

## 5. Charts

- Candles Up: `#00FFA3`
- Candles Down: `#FF4D4D`
- Volume Bars: `#334155`
- Grid: `#1F2933`
- Crosshair: `#94A3B8`

---

## 6. Typography

### Fonts
- UI Font: `Inter`
- Numbers / Trading: `JetBrains Mono`

### Sizes
- H1: 24px
- H2: 20px
- H3: 16px
- Body: 14px
- Small: 12px

---

## 7. Spacing & Radius

- Base Spacing: 4px
- Card Padding: 16px
- Section Gap: 24px
- Border Radius:
  - Small: 6px
  - Medium: 10px
  - Large: 14px

---

## 8. Shadows & Glow

- Card Shadow: `0 0 12px rgba(0, 0, 0, 0.4)`
- Neon Glow (Active): `0 0 8px rgba(34, 211, 238, 0.6)`
- PnL Glow Green: `0 0 10px rgba(0, 255, 163, 0.5)`
- PnL Glow Red: `0 0 10px rgba(255, 77, 77, 0.5)`

---

## 9. State Colors

| State        | Color      |
|---------------|------------|
| Active        | #22D3EE    |
| Inactive      | #6B7280    |
| Success       | #00FFA3    |
| Error         | #FF4D4D    |
| Warning       | #FACC15    |
| Processing    | #A78BFA    |

---

## 10. RTL Support (Arabic)

- Всички spacing токени използват logical properties:
  - margin-inline-start
  - padding-inline-end
- Sidebar и навигация се обръщат хоризонтално
- Шрифтът остава същият (Inter поддържа Arabic)

---

## 11. Mapping to Tailwind

Токените ще бъдат имплементирани в:

