# SECURITY.md — Security Guidelines for DEX Trading Platform

## 1. Overview

Тази платформа е **non-custodial, multi-chain DEX-only trading system**.  
Целта е да се осигури безопасност при изпълнение на транзакции, защита на ключове и данни, и минимизиране на риска от грешки и атаки.

---

## 2. Key Management

- **Private keys се съхраняват локално** и никога не се commit-ват в git.  
- `.env` съдържа private key и се добавя в `.gitignore`.  
- Препоръчва се **ENCRYPT_SECRETS=true** за локално криптиране на ключовете.  
- Transaction signing се извършва **on-client**, non-custodial.  

---

## 3. RPC & Network Security

- Всички RPC URLs и WebSocket endpoints са зададени в `.env` и са read-only там, където е възможно.  
- Препоръчва се използване на **HTTPS / WSS** връзки за всички блокчейн мрежи.  
- Rate limiting на RPC calls трябва да се следи, за да се избегне блокиране от провайдърите.  

---

## 4. Execution & Risk Safety

- **Adaptive SL/TP**, max leverage и max open positions се конфигурират през `.env`.  
- **Shadow/Research Engine** позволява тестване на стратегии без реални средства.  
- MEV protection и Flashbots relay integration минимизират фронт-раннинг рискове.  
- Всички транзакции логват: block number, tx hash, strategy, PnL, risk exposure.  

---

## 5. Failover & Redundancy

- Core Engine и Shadow Engine могат да се стартират независимо.  
- При crash или RPC failure:
  - Retry логика с exponential backoff
  - Logging на грешките в `logs/` директорията
- Регулярни бекапи на DB (`data/trading.db`) препоръчителни.  

---

## 6. Monitoring & Alerts

- **Prometheus metrics**: open positions, executed trades, PnL, error rates.  
- Alerts могат да се конфигурират през `.env` (например Telegram).  
- Логовете използват **loguru + rich** за удобен review.  

---

## 7. Development Best Practices

- Никога не commit-вайте `.env` или private keys.  
- Всеки нов модул/функция трябва да преминава shadow/paper testing.  
- Използвайте виртуално окръжение (`.venv`) и `requirements.txt` за контрол на dependencies.  
- Code review и modular design за plug-and-play стратегии и филтри.  

---

## 8. Security Notes

- Платформата е **non-custodial** — потребителите държат ключовете си локално.  
- Архитектурата позволява добавяне на нови chains, но те трябва да следват същите безопасни интерфейси.  
- Regular updates на Python библиотеки и Web3 пакети се препоръчват за patch-ове на сигурността.  
- Никога не споделяйте `.env` или лог файлове с чувствителна информация публично.  

---

## 9. Conclusion

Сигурността е заложена на ниво:

- Key management
- Transaction execution
- Risk & failover
- Monitoring & alerting

Следването на тези правила гарантира безопасна и стабилна работа на DEX Trading Platform.
