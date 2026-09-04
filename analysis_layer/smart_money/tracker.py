# analysis_layer/smart_money/tracker.py
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SmartMoneyTracker:
    """تتبع سلوك المؤسسات"""
    
    def __init__(self, smc_analyzer):
        self.smc = smc_analyzer
        self.history = []
    
    def analyze(self, df):
        if len(df) < 20:
            return {'score': 0, 'activity': 'NEUTRAL', 'insight': 'بيانات غير كافية'}
        
        smc_result = self.smc.analyze(df)
        
        score = 0
        liq = smc_result.get('liquidity_zones', {})
        
        if liq.get('ssl_swept'):
            score += 30
        if liq.get('bsl_swept'):
            score -= 30
        
        structure = smc_result.get('structure', 'CONSOLIDATION')
        if structure == 'UPTREND':
            score += 20
        elif structure == 'DOWNTREND':
            score -= 20
        
        obs = smc_result.get('order_blocks', {})
        if obs.get('bullish'):
            score += obs['bullish']['strength'] * 0.2
        if obs.get('bearish'):
            score -= obs['bearish']['strength'] * 0.2
        
        session = smc_result.get('session', 'OFF_SESSION')
        if session in ['LONDON', 'NEW_YORK', 'KILL_ZONE']:
            score += 10
        
        self.history.append({
            'time': datetime.now(),
            'score': score,
            'price': df.iloc[-1]['close']
        })
        if len(self.history) > 100:
            self.history.pop(0)
        
        insight = self._generate_insight(score)
        
        return {
            'score': round(score, 1),
            'activity': 'BULLISH' if score > 30 else 'BEARISH' if score < -30 else 'NEUTRAL',
            'smc_result': smc_result,
            'insight': insight
        }
    
    def _generate_insight(self, score):
        if score > 40:
            return "🔥 نشاط شرائي مؤسسي قوي"
        elif score > 20:
            return "📈 ميل شرائي معتدل"
        elif score > -20:
            return "⚖️ نشاط متوازن"
        elif score > -40:
            return "📉 ميل بيعي معتدل"
        return "❄️ نشاط بيعي مؤسسي قوي"
