"""
Signal Grid Bot - Telegram Signal Follower with Grid Strategy
Adapted for DEX (Hyperliquid Futures)

Features:
- Parses trading signals from Telegram channels
- Grid entry strategy (5 levels)
- Grid exit strategy (5 TP zones)
- Smart signal validation
- Risk management with emergency stop
- Works on Hyperliquid (Arbitrum DEX Futures)
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import re

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Signal types"""
    LONG = "long"
    SHORT = "short"
    UNKNOWN = "unknown"


class SignalParser:
    """Parse trading signals from text (Telegram messages)"""
    
    SIGNAL_PATTERNS = {
        'long': r'(\w+)\s+(LONG|Long)',
        'short': r'(\w+)\s+(SHORT|Short)',
        'near_long': r'Near\s+Long',
        'near_short': r'Near\s+Short',
    }
    
    # Coin mapping to standard symbols
    COIN_MAPPING = {
        'BTC': 'BTC/USDT',
        'ETH': 'ETH/USDT',
        'NEAR': 'NEAR/USDT',
        'DOG': 'DOGE/USDT',
        'DODGE': 'DOGE/USDT',
        'SOL': 'SOL/USDT',
        'AVAX': 'AVAX/USDT',
        'MATIC': 'MATIC/USDT',
        # Add more as needed
    }
    
    def parse(self, text: str) -> Optional[Dict]:
        """
        Parse signal from text
        
        Examples:
        - "BTC LONG" -> {type: LONG, coin: BTC/USDT}
        - "NEAR Short" -> {type: SHORT, coin: NEAR/USDT}
        - "DODGE, LONG" -> {type: LONG, coin: DOGE/USDT}
        """
        text = text.upper().strip()
        
        # Detect signal type
        if 'LONG' in text:
            signal_type = SignalType.LONG
        elif 'SHORT' in text:
            signal_type = SignalType.SHORT
        else:
            return None
        
        # Extract coin
        coin = self._extract_coin(text)
        if not coin:
            return None
        
        # Map to standard symbol
        symbol = self.COIN_MAPPING.get(coin, f"{coin}/USDT")
        
        return {
            'type': signal_type,
            'symbol': symbol,
            'coin': coin,
            'raw_text': text,
            'timestamp': datetime.now(),
            'confidence': self._calculate_confidence(text)
        }
    
    def _extract_coin(self, text: str) -> Optional[str]:
        """Extract coin symbol from text"""
        # Remove common words
        skip_words = ['LONG', 'SHORT', 'NEAR', 'SWING', 'ALT', 'V2', 'THE']
        
        words = text.replace(',', ' ').split()
        
        for word in words:
            clean_word = word.strip('.,!?;:')
            if clean_word not in skip_words and len(clean_word) > 1:
                # Check if it's a known coin
                if clean_word in self.COIN_MAPPING:
                    return clean_word
                # Return first unknown word (might be new coin)
                if len(clean_word) <= 6:  # Max coin symbol length
                    return clean_word
        
        return None
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate signal confidence (0.0 to 1.0)"""
        confidence = 0.5  # Base confidence
        
        # More confidence if explicit
        if text.count('LONG') + text.count('SHORT') == 1:
            confidence += 0.2
        
        # More confidence if has specific coin name
        if any(coin in text for coin in self.COIN_MAPPING.keys()):
            confidence += 0.2
        
        # Less confidence if ambiguous
        if '?' in text or 'MAYBE' in text:
            confidence -= 0.3
        
        return max(0.0, min(1.0, confidence))


class SignalValidator:
    """Validate signals before execution"""
    
    def __init__(self, exchange):
        self.exchange = exchange
    
    def validate(self, signal: Dict) -> Tuple[bool, str]:
        """
        Validate signal
        
        Returns: (is_valid, reason)
        """
        # 1. Check confidence
        if signal['confidence'] < 0.5:
            return False, "Low confidence signal"
        
        # 2. Check if symbol exists
        try:
            ticker = self.exchange.fetch_ticker(signal['symbol'])
            if not ticker:
                return False, f"Symbol {signal['symbol']} not found"
        except Exception as e:
            return False, f"Symbol validation error: {e}"
        
        # 3. Check market conditions
        try:
            # Get recent candles
            candles = self.exchange.fetch_ohlcv(
                signal['symbol'], 
                '1h', 
                limit=24
            )
            
            # Check volatility (ATR)
            volatility = self._calculate_volatility(candles)
            
            if volatility > 10:  # More than 10% volatility
                return False, "Market too volatile"
            
            if volatility < 0.5:  # Less than 0.5% volatility
                return False, "Market too stagnant"
            
        except Exception as e:
            logger.warning(f"Market condition check failed: {e}")
            # Continue anyway
        
        # 4. Check volume
        try:
            volume_24h = ticker.get('quoteVolume', 0)
            if volume_24h < 1000000:  # Less than $1M daily volume
                return False, "Low liquidity"
        except:
            pass
        
        return True, "Valid signal"
    
    def _calculate_volatility(self, candles: List) -> float:
        """Calculate ATR as volatility measure"""
        if len(candles) < 14:
            return 0
        
        atr_sum = 0
        for i in range(1, min(14, len(candles))):
            high = candles[i][2]
            low = candles[i][3]
            prev_close = candles[i-1][4]
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            atr_sum += tr
        
        atr = atr_sum / 14
        current_price = candles[-1][4]
        
        return (atr / current_price) * 100  # ATR as percentage


class GridCalculator:
    """Calculate grid levels for entry and exit"""
    
    @staticmethod
    def calculate_entry_grid(
        current_price: float,
        signal_type: SignalType,
        num_levels: int = 5,
        spacing_percent: float = 2.0,
        volatility: float = 1.0
    ) -> List[float]:
        """
        Calculate entry grid levels
        
        For LONG: Place buy orders below current price
        For SHORT: Place sell orders above current price
        """
        # Adjust spacing based on volatility
        adjusted_spacing = spacing_percent * (1 + volatility / 5)
        
        levels = []
        
        if signal_type == SignalType.LONG:
            # Buy orders below current price
            for i in range(num_levels):
                level_price = current_price * (1 - (adjusted_spacing / 100) * (i + 1))
                levels.append(round(level_price, 2))
        
        else:  # SHORT
            # Sell orders above current price
            for i in range(num_levels):
                level_price = current_price * (1 + (adjusted_spacing / 100) * (i + 1))
                levels.append(round(level_price, 2))
        
        return levels
    
    @staticmethod
    def calculate_exit_grid(
        entry_price: float,
        signal_type: SignalType,
        num_zones: int = 5,
        target_profit_percent: float = 5.0
    ) -> List[Dict]:
        """
        Calculate TP zones
        
        Returns: List of {price, percent_to_close}
        """
        zones = []
        percent_per_zone = 100 / num_zones  # Split equally
        
        for i in range(1, num_zones + 1):
            if signal_type == SignalType.LONG:
                # TP levels above entry
                tp_price = entry_price * (1 + (target_profit_percent / 100) * (i / num_zones))
            else:  # SHORT
                # TP levels below entry
                tp_price = entry_price * (1 - (target_profit_percent / 100) * (i / num_zones))
            
            zones.append({
                'price': round(tp_price, 2),
                'percent': percent_per_zone,
                'zone_number': i
            })
        
        return zones


class SignalGridBot:
    """
    Main Signal Grid Bot
    
    How it works:
    1. Receives signal from Telegram
    2. Validates signal
    3. Places 5 entry orders (grid)
    4. Places 5 TP orders (grid)
    5. Monitors and manages position
    """
    
    def __init__(
        self,
        user_id: int,
        exchange,
        leverage: int = 3,
        risk_per_trade_percent: float = 2.0,
        max_leverage: int = 5,
        emergency_stop_percent: float = 15.0
    ):
        self.user_id = user_id
        self.exchange = exchange
        self.leverage = min(leverage, max_leverage)  # Cap leverage for safety
        self.risk_per_trade = risk_per_trade_percent
        self.emergency_stop = emergency_stop_percent
        
        self.parser = SignalParser()
        self.validator = SignalValidator(exchange)
        self.grid_calc = GridCalculator()
        
        self.active_positions = {}
        self.signal_history = []
        
        logger.info(f"SignalGridBot initialized for user {user_id}")
    
    def process_signal(self, signal_text: str) -> bool:
        """
        Process incoming signal
        
        Returns: True if signal was executed
        """
        try:
            # 1. Parse signal
            signal = self.parser.parse(signal_text)
            
            if not signal:
                logger.warning(f"Could not parse signal: {signal_text}")
                return False
            
            logger.info(f"📊 Parsed signal: {signal['coin']} {signal['type'].value.upper()}")
            
            # 2. Validate signal
            is_valid, reason = self.validator.validate(signal)
            
            if not is_valid:
                logger.warning(f"❌ Signal rejected: {reason}")
                return False
            
            logger.info(f"✅ Signal validated: {reason}")
            
            # 3. Check if we already have position
            if signal['symbol'] in self.active_positions:
                logger.warning(f"Already have position in {signal['symbol']}")
                return False
            
            # 4. Execute signal
            success = self._execute_signal(signal)
            
            # 5. Log signal
            self.signal_history.append({
                'signal': signal,
                'executed': success,
                'timestamp': datetime.now()
            })
            
            return success
        
        except Exception as e:
            logger.error(f"Signal processing error: {e}", exc_info=True)
            return False
    
    def _execute_signal(self, signal: Dict) -> bool:
        """Execute trading signal with grid strategy"""
        try:
            symbol = signal['symbol']
            signal_type = signal['type']
            
            # Get current price
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            logger.info(f"💰 Current price: {current_price}")
            
            # Get account balance
            balance = self.exchange.fetch_balance()
            available_capital = balance['USDT']['free']
            
            # Calculate position size (risk management)
            position_size_usd = available_capital * (self.risk_per_trade / 100)
            
            logger.info(f"📊 Position size: ${position_size_usd:.2f} ({self.risk_per_trade}% of capital)")
            
            # Calculate volatility for grid spacing
            candles = self.exchange.fetch_ohlcv(symbol, '1h', limit=24)
            volatility = self.validator._calculate_volatility(candles)
            
            # Calculate entry grid
            entry_levels = self.grid_calc.calculate_entry_grid(
                current_price=current_price,
                signal_type=signal_type,
                num_levels=5,
                spacing_percent=2.0,
                volatility=volatility
            )
            
            logger.info(f"📍 Entry levels: {entry_levels}")
            
            # Place entry orders
            entry_orders = []
            amount_per_level = (position_size_usd / len(entry_levels)) / current_price
            
            for level_price in entry_levels:
                try:
                    order = self.exchange.create_limit_order(
                        symbol=symbol,
                        side='buy' if signal_type == SignalType.LONG else 'sell',
                        amount=amount_per_level,
                        price=level_price
                    )
                    entry_orders.append(order)
                    logger.info(f"✅ Entry order placed at ${level_price}")
                except Exception as e:
                    logger.error(f"Failed to place entry order: {e}")
            
            if not entry_orders:
                return False
            
            # Calculate average entry price
            avg_entry = sum(entry_levels) / len(entry_levels)
            
            # Calculate TP grid
            tp_zones = self.grid_calc.calculate_exit_grid(
                entry_price=avg_entry,
                signal_type=signal_type,
                num_zones=5,
                target_profit_percent=5.0
            )
            
            logger.info(f"🎯 TP zones: {[z['price'] for z in tp_zones]}")
            
            # Calculate stop loss
            if signal_type == SignalType.LONG:
                stop_loss = avg_entry * 0.97  # 3% below entry
            else:
                stop_loss = avg_entry * 1.03  # 3% above entry
            
            logger.info(f"🛑 Stop loss: ${stop_loss:.2f}")
            
            # Store position
            self.active_positions[symbol] = {
                'signal': signal,
                'signal_type': signal_type,
                'entry_orders': entry_orders,
                'entry_levels': entry_levels,
                'avg_entry': avg_entry,
                'tp_zones': tp_zones,
                'stop_loss': stop_loss,
                'position_size': position_size_usd,
                'leverage': self.leverage,
                'opened_at': datetime.now(),
                'status': 'active'
            }
            
            logger.info(f"✅ Signal executed successfully: {symbol} {signal_type.value.upper()}")
            
            return True
        
        except Exception as e:
            logger.error(f"Signal execution error: {e}", exc_info=True)
            return False
    
    def monitor_positions(self):
        """Monitor and manage active positions"""
        for symbol, position in list(self.active_positions.items()):
            try:
                self._check_position(symbol, position)
            except Exception as e:
                logger.error(f"Position monitoring error for {symbol}: {e}")
    
    def _check_position(self, symbol: str, position: Dict):
        """Check individual position for TP/SL"""
        try:
            # Get current price
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            signal_type = position['signal_type']
            avg_entry = position['avg_entry']
            
            # Calculate current P&L
            if signal_type == SignalType.LONG:
                pnl_percent = ((current_price - avg_entry) / avg_entry) * 100
            else:
                pnl_percent = ((avg_entry - current_price) / avg_entry) * 100
            
            # Check emergency stop
            if pnl_percent <= -self.emergency_stop:
                logger.warning(f"🚨 EMERGENCY STOP: {symbol} loss {pnl_percent:.2f}%")
                self._close_position(symbol, position, "Emergency stop")
                return
            
            # Check stop loss
            if signal_type == SignalType.LONG:
                if current_price <= position['stop_loss']:
                    logger.info(f"🛑 Stop loss hit: {symbol}")
                    self._close_position(symbol, position, "Stop loss")
                    return
            else:
                if current_price >= position['stop_loss']:
                    logger.info(f"🛑 Stop loss hit: {symbol}")
                    self._close_position(symbol, position, "Stop loss")
                    return
            
            # Check TP zones
            for zone in position['tp_zones']:
                if signal_type == SignalType.LONG:
                    if current_price >= zone['price'] and not zone.get('executed'):
                        self._take_partial_profit(symbol, position, zone)
                else:
                    if current_price <= zone['price'] and not zone.get('executed'):
                        self._take_partial_profit(symbol, position, zone)
        
        except Exception as e:
            logger.error(f"Position check error: {e}")
    
    def _take_partial_profit(self, symbol: str, position: Dict, zone: Dict):
        """Take profit at zone level"""
        try:
            percent_to_close = zone['percent'] / 100
            
            # Close portion of position
            logger.info(f"💰 Taking {zone['percent']}% profit at ${zone['price']} (Zone {zone['zone_number']})")
            
            zone['executed'] = True
            zone['executed_at'] = datetime.now()
            
            # Check if all zones executed
            all_executed = all(z.get('executed', False) for z in position['tp_zones'])
            if all_executed:
                logger.info(f"✅ All TP zones hit for {symbol}")
                self._close_position(symbol, position, "All TPs hit")
        
        except Exception as e:
            logger.error(f"Take profit error: {e}")
    
    def _close_position(self, symbol: str, position: Dict, reason: str):
        """Close position completely"""
        try:
            logger.info(f"🔒 Closing position {symbol}: {reason}")
            
            # Cancel any pending orders
            # Close position
            # Update position status
            
            position['status'] = 'closed'
            position['closed_at'] = datetime.now()
            position['close_reason'] = reason
            
            # Remove from active
            del self.active_positions[symbol]
            
            logger.info(f"✅ Position closed: {symbol}")
        
        except Exception as e:
            logger.error(f"Close position error: {e}")
    
    def get_stats(self) -> Dict:
        """Get bot statistics"""
        total_signals = len(self.signal_history)
        executed_signals = sum(1 for s in self.signal_history if s['executed'])
        
        return {
            'user_id': self.user_id,
            'total_signals': total_signals,
            'executed_signals': executed_signals,
            'execution_rate': executed_signals / total_signals if total_signals > 0 else 0,
            'active_positions': len(self.active_positions),
            'leverage': self.leverage,
            'risk_per_trade': self.risk_per_trade
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Mock exchange (replace with real Hyperliquid connection)
    class MockExchange:
        def fetch_ticker(self, symbol):
            return {'last': 30000}
        
        def fetch_ohlcv(self, symbol, timeframe, limit):
            return [[0, 30000, 31000, 29000, 30000, 1000] for _ in range(limit)]
        
        def fetch_balance(self):
            return {'USDT': {'free': 10000}}
        
        def create_limit_order(self, symbol, side, amount, price):
            return {'id': '123', 'status': 'open'}
    
    # Initializ
