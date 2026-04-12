import { useState, useEffect, useRef, useCallback } from "react";
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from "recharts";

// \u2500\u2500\u2500 CONFIG \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
const API_BASE = "http://localhost:8080";
const API_TOKEN = "aegis-dev-token";
const POLL_MS = 6000;

// \u2500\u2500\u2500 i18n \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
const T = {
  en: {
    dashboard: "Dashboard", trading: "Trading", positions: "Positions",
    risk: "Risk Monitor", referral: "Referral", settings: "Settings",
    status: "Status", uptime: "Uptime", mode: "Mode", balance: "Balance",
    totalPnl: "Total PnL", winRate: "Win Rate", trades: "Trades",
    startBot: "Start Bot", stopBot: "Stop Bot", liveMode: "Live",
    paperMode: "Paper", dryMode: "Dry Run", symbol: "Symbol",
    side: "Side", size: "Size", entryPrice: "Entry Price",
    unrealizedPnl: "Unrealized PnL", leverage: "Leverage",
    maxDrawdown: "Max Drawdown", exposure: "Exposure",
    openPositions: "Open Positions", dailyLoss: "Daily Loss",
    referralCode: "Referral Code", totalRefs: "Total Referrals",
    referralEarnings: "Earnings", generateCode: "Generate Code",
    slippage: "Slippage %", maxPos: "Max Positions",
    riskPct: "Risk %", saveSettings: "Save Settings",
    running: "RUNNING", stopped: "STOPPED", connecting: "\u2026",
    pnlHistory: "PnL History", noPositions: "No open positions",
    copy: "Copy", copied: "Copied!",
  },
  bg: {
    dashboard: "\u0422\u0430\u0431\u043b\u043e", trading: "\u0422\u044a\u0440\u0433\u043e\u0432\u0438\u044f", positions: "\u041f\u043e\u0437\u0438\u0446\u0438\u0438",
    risk: "\u0420\u0438\u0441\u043a \u041c\u043e\u043d\u0438\u0442\u043e\u0440", referral: "\u0420\u0435\u0444\u0435\u0440\u0430\u043b\u0438", settings: "\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438",
    status: "\u0421\u0442\u0430\u0442\u0443\u0441", uptime: "\u0420\u0430\u0431\u043e\u0442\u043d\u043e \u0432\u0440\u0435\u043c\u0435", mode: "\u0420\u0435\u0436\u0438\u043c", balance: "\u0411\u0430\u043b\u0430\u043d\u0441",
    totalPnl: "\u041e\u0431\u0449 PnL", winRate: "Win Rate", trades: "\u0421\u0434\u0435\u043b\u043a\u0438",
    startBot: "\u0421\u0442\u0430\u0440\u0442", stopBot: "\u0421\u0442\u043e\u043f", liveMode: "\u0416\u0438\u0432\u043e",
    paperMode: "\u0425\u0430\u0440\u0442\u0438\u044f", dryMode: "\u0422\u0435\u0441\u0442", symbol: "\u0410\u043a\u0442\u0438\u0432",
    side: "\u041f\u043e\u0441\u043e\u043a\u0430", size: "\u0420\u0430\u0437\u043c\u0435\u0440", entryPrice: "\u0412\u0445. \u0426\u0435\u043d\u0430",
    unrealizedPnl: "\u041d\u0435\u0440\u0435\u0430\u043b\u0438\u0437\u0438\u0440\u0430\u043d PnL", leverage: "\u041b\u0438\u0432\u044a\u0440\u0438\u0434\u0436",
    maxDrawdown: "\u041c\u0430\u043a\u0441. Drawdown", exposure: "\u0415\u043a\u0441\u043f\u043e\u0437\u0438\u0446\u0438\u044f",
    openPositions: "\u041e\u0442\u0432\u043e\u0440\u0435\u043d\u0438 \u043f\u043e\u0437\u0438\u0446\u0438\u0438", dailyLoss: "\u0414\u043d\u0435\u0432\u043d\u0430 \u0437\u0430\u0433\u0443\u0431\u0430",
    referralCode: "\u0420\u0435\u0444\u0435\u0440\u0430\u043b\u0435\u043d \u043a\u043e\u0434", totalRefs: "\u041e\u0431\u0449\u043e \u0440\u0435\u0444\u0435\u0440\u0430\u043b\u0438",
    referralEarnings: "\u041f\u0440\u0438\u0445\u043e\u0434\u0438", generateCode: "\u0413\u0435\u043d\u0435\u0440\u0438\u0440\u0430\u0439 \u043a\u043e\u0434",
    slippage: "\u041f\u043b\u044a\u0437\u0433\u0430\u043d\u0435 %", maxPos: "\u041c\u0430\u043a\u0441. \u043f\u043e\u0437\u0438\u0446\u0438\u0438",
    riskPct: "\u0420\u0438\u0441\u043a %", saveSettings: "\u0417\u0430\u043f\u0430\u0437\u0438",
    running: "\u0410\u041a\u0422\u0418\u0412\u0415\u041d", stopped: "\u0421\u041f\u0420\u042f\u041d", connecting: "\u2026",
    pnlHistory: "\u0418\u0441\u0442\u043e\u0440\u0438\u044f PnL", noPositions: "\u041d\u044f\u043c\u0430 \u043e\u0442\u0432\u043e\u0440\u0435\u043d\u0438 \u043f\u043e\u0437\u0438\u0446\u0438\u0438",
    copy: "\u041a\u043e\u043f\u0438\u0440\u0430\u0439", copied: "\u041a\u043e\u043f\u0438\u0440\u0430\u043d\u043e!",
  },
};

// \u2500\u2500\u2500 AUDIO \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
function useAudio() {
  const ctx = useRef(null);
  const getCtx = () => {
    if (!ctx.current) ctx.current = new (window.AudioContext || window.webkitAudioContext)();
    return ctx.current;
  };
  const beep = useCallback((freq = 440, dur = 0.12, type = "sine", vol = 0.18) => {
    try {
      const ac = getCtx();
      const osc = ac.createOscillator();
      const gain = ac.createGain();
      osc.connect(gain); gain.connect(ac.destination);
      osc.type = type; osc.frequency.value = freq;
      gain.gain.setValueAtTime(vol, ac.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ac.currentTime + dur);
      osc.start(); osc.stop(ac.currentTime + dur);
    } catch (_) {}
  }, []);
  return {
    tradeBuy: () => { beep(660, 0.08); setTimeout(() => beep(880, 0.1), 80); },
    tradeSell: () => { beep(440, 0.08, "sawtooth"); setTimeout(() => beep(330, 0.1, "sawtooth"), 80); },
    alert: () => { beep(880, 0.06); setTimeout(() => beep(880, 0.06), 120); setTimeout(() => beep(660, 0.1), 240); },
    click: () => beep(600, 0.05, "square", 0.08),
  };
}

// \u2500\u2500\u2500 API \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
async function api(path, method = "GET", body = null) {
  const opts = {
    method,
    headers: { "Authorization": `Bearer ${API_TOKEN}`, "Content-Type": "application/json" },
  };
  if (body) opts.body = JSON.stringify(body);
  try {
    const r = await fetch(`${API_BASE}${path}`, opts);
    if (!r.ok) return null;
    return await r.json();
  } catch { return null; }
}

//
