# analysis_layer/technical/smc_analyzer.py
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class SMCAnalyzer:
    """محرك التحليل الفني SMC/ICT"""
    
    def __init__(self):
        self.session_times = {
            'london': (7, 16),
            'ny': (12, 20),
            'killzone': (13, 16)
        }
    
    def analyze(self, df):
        if len(df) < 20:
            return {'error': 'بيانات غير كافية'}
        
        result = {
            'structure': self._detect_structure(df),
            'liquidity_zones': self._find_liquidity(df),
            'order_blocks': self._find_order_blocks(df),
            'fvg_zones': self._find_fvg(df),
            'session': self._get_current_session(),
            'bias': None,
            'key_levels': self._find_key_levels(df)
        }
        result['bias'] = self._determine_bias(result)
        return result
    
    def _detect_structure(self, df):
        closes = df['close'].values[-20:]
        highs = df['high'].values[-20:]
        lows = df['low'].values[-20:]
        
        uptrend = closes[-1] > max(highs[-5:]) and closes[-2] > max(highs[-6:-1])
        downtrend = closes[-1] < min(lows[-5:]) and closes[-2] < min(lows[-6:-1])
        
        if uptrend:
            return 'UPTREND'
        elif downtrend:
            return 'DOWNTREND'
        return 'CONSOLIDATION'
    
    def _find_liquidity(self, df):
        highs = df['high'].values[-20:]
        lows = df['low'].values[-20:]
        closes = df['close'].values
        current_price = closes[-1]
        
        bsl = max(highs)
        ssl = min(lows)
        last_high = max(highs[-3:])
        last_low = min(lows[-3:])
        
        ssl_swept = current_price < last_low and current_price > min(lows[-10:-3]) if len(lows) > 10 else False
        bsl_swept = current_price > last_high and current_price < max(highs[-10:-3]) if len(highs) > 10 else False
        
        return {
            'bsl': round(bsl, 2),
            'ssl': round(ssl, 2),
            'ssl_swept': ssl_swept,
            'bsl_swept': bsl_swept
        }
    
    def _find_order_blocks(self, df):
        closes = df['close'].values
        opens = df['open'].values
        highs = df['high'].values
        lows = df['low'].values
        
        bullish_obs = []
        bearish_obs = []
        
        for i in range(-20, -1):
            if i < 2:
                continue
            move = abs(closes[i] - opens[i])
            avg_move = np.mean([abs(closes[j] - opens[j]) for j in range(max(-20, i-10), i)]) if i > -10 else move
            
            if move > avg_move * 1.8:
                if closes[i] > opens[i]:
                    wick_ratio = (highs[i] - closes[i]) / (highs[i] - lows[i]) if (highs[i] - lows[i]) > 0 else 0
                    if wick_ratio > 0.4:
                        bullish_obs.append({
                            'high': round(highs[i], 2),
                            'low': round(lows[i], 2),
                            'strength': min(100, 50 + wick_ratio * 50)
                        })
                else:
                    wick_ratio = (opens[i] - lows[i]) / (highs[i] - lows[i]) if (highs[i] - lows[i]) > 0 else 0
                    if wick_ratio > 0.4:
                        bearish_obs.append({
                            'high': round(highs[i], 2),
                            'low': round(lows[i], 2),
                            'strength': min(100, 50 + wick_ratio * 50)
                        })
        
        return {
            'bullish': max(bullish_obs, key=lambda x: x['strength']) if bullish_obs else None,
            'bearish': max(bearish_obs, key=lambda x: x['strength']) if bearish_obs else None
        }
    
    def _find_fvg(self, df):
        highs = df['high'].values[-15:]
        lows = df['low'].values[-15:]
        
        fvg_bullish = []
        fvg_bearish = []
        
        for i in range(2, len(highs)):
            if lows[i] > highs[i-2]:
                fvg_bullish.append({
                    'high': round(lows[i], 2),
                    'low': round(highs[i-2], 2),
                    'size': round(lows[i] - highs[i-2], 2)
                })
            if highs[i] < lows[i-2]:
                fvg_bearish.append({
                    'high': round(lows[i-2], 2),
                    'low': round(highs[i], 2),
                    'size': round(lows[i-2] - highs[i], 2)
                })
        
        return {
            'bullish': fvg_bullish[-1] if fvg_bullish else None,
            'bearish': fvg_bearish[-1] if fvg_bearish else None
        }
    
    def _get_current_session(self):
        now = datetime.now(timezone.utc)
        hour = now.hour
        
        if self.session_times['killzone'][0] <= hour < self.session_times['killzone'][1]:
            return 'KILL_ZONE'
        elif self.session_times['london'][0] <= hour < self.session_times['london'][1]:
            return 'LONDON'
        elif self.session_times['ny'][0] <= hour < self.session_times['ny'][1]:
            return 'NEW_YORK'
        return 'OFF_SESSION'
    
    def _determine_bias(self, analysis):
        score = 0
        liq = analysis['liquidity_zones']
        obs = analysis['order_blocks']
        
        if analysis['structure'] == 'UPTREND':
            score += 30
        elif analysis['structure'] == 'DOWNTREND':
            score -= 30
        
        if liq['ssl_swept']:
            score += 25
        if liq['bsl_swept']:
            score -= 25
        
        if obs['bullish']:
            score += obs['bullish']['strength'] * 0.2
        if obs['bearish']:
            score -= obs['bearish']['strength'] * 0.2
        
        return 'BULLISH' if score > 25 else 'BEARISH' if score < -25 else 'NEUTRAL'
    
    def _find_key_levels(self, df):
        highs = df['high'].values[-100:]
        lows = df['low'].values[-100:]
        
        resistance = []
        support = []
        
        for i in range(2, len(highs)-2):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1] and highs[i] > highs[i-2]:
                resistance.append(highs[i])
            if lows[i] < lows[i-1] and lows[i] < lows[i+1] and lows[i] < lows[i-2]:
                support.append(lows[i])
        
        current = df['close'].iloc[-1]
        resistance = sorted([r for r in resistance if r > current])[:5]
        support = sorted([s for s in support if s < current], reverse=True)[:5]
        
        return {
            'resistance': [round(r, 2) for r in resistance],
            'support': [round(s, 2) for s in support]
          }
