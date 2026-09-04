# presentation_layer/alerts.py
import logging

logger = logging.getLogger(__name__)

class AlertSystem:
    """نظام التنبيهات"""
    
    def __init__(self):
        self.alert_thresholds = {
            'price_breakout': 5,
            'volume_spike': 2.5,
            'liquidity_sweep': True,
            'news_impact': 'HIGH'
        }
        self.active_alerts = []
    
    def check_alerts(self, df, smc_result, news):
        alerts = []
        current_price = df.iloc[-1]['close']
        
        key_levels = smc_result.get('key_levels', {})
        for level in key_levels.get('resistance', []):
            if current_price > level:
                alerts.append({
                    'type': 'BREAKOUT',
                    'direction': 'UP',
                    'level': level,
                    'message': f"🚀 اختراق مقاومة {level:.2f}"
                })
        
        liq = smc_result.get('liquidity_zones', {})
        if liq.get('ssl_swept'):
            alerts.append({
                'type': 'LIQUIDITY_SWEEP',
                'direction': 'BULLISH',
                'message': "🎯 تم صيد سيولة البيع (SSL)"
            })
        
        self.active_alerts = alerts
        return alerts
    
    def get_active_alerts(self):
        return self.active_alerts
