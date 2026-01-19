
**Explanation:**
1. Market Data Aggregator:
   - Събира on-chain и read-only off-chain данни
   - Осигурява normalized view за всички стратегии
2. Signal Generator:
   - Извлича входни точки за всяка стратегия
3. Filter Stack:
   - Модулно включва / изключва филтри (volatility, regime, funding, time-of-day)
4. Risk Engine:
   - Adaptive position sizing, max leverage, SL/TP, daily drawdown
5. Execution Engine:
   - Multi-chain DEX routing
   - MEV protection
   - Slippage control
6. Trade Logger → Analytics:
   - Пълна история, shadow/paper mode, backtesting, performance charts

---

## 4. Modules Interaction

- **Core Engine** – управлява lifecycle на всички модули  
- **Strategy Modules** – plug-and-play, могат да се добавят нови без промяна в core  
- **Filter Stack** – филтрират сигнали преди risk check  
- **Risk Engine** – гарантира правилно position sizing и управление на drawdowns  
- **Execution Engine** – изпълнява транзакции през DEX, подпомага multi-chain routing  
- **Shadow/Research Engine** – работи паралелно за симулации и оптимизация  
- **Monitoring** – Prometheus, alerts, логове с loguru/rich

---

## 5. Multi-Chain Support

- Всеки chain има собствен RPC и DEX router
- Execution Engine е абстрактен слой:
  - `dex_router.py` избира правилния контракт според chain и token
  - Може да се добавят нови chains без промяна на логиката

---

## 6. Risk & Safety

- Adaptive SL/TP
- Max daily drawdown
- Max open positions
- Shadow trading engine за нови стратегии
- MEV protection
- Logging и Prometheus metrics

---

## 7. Environment & Deployment

- `.env` съдържа всички ключове, RPC и конфигурации
- `run.sh` стартира всички модули автоматично
- Logging → `logs/`
- Data → `data/`
- Python virtualenv `.venv` + `requirements.txt`

---

## 8. Security Considerations

- Private keys се пазят локално и никога не се commit-ват
- Encrypted secrets optional (ENCRYPT_SECRETS=true)
- Transaction signing on-client, non-custodial
- MEV protection & flashbots relay integration

---

## 9. Extensibility

- Нови стратегии → добавят се в `/strategies`, plug-and-play
- Нови филтри → добавят се в `/filters`, активирани чрез `.env`
- Нови chains → добавят се в `/execution/dex_router.py` и `.env`

---

**Conclusion:**  
Тази архитектура е **модулна, безопасна, multi-chain и готова за автоматизация на DEX търговия**. Всички нови функционалности (analytics, shadow trading, filters, risk engine) се надграждат върху стабилното core, без да чупят съществуващата система.
