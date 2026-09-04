# presentation_layer/reports.py
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    """توليد التقارير"""
    
    def generate_report(self, analysis_data):
        return {
            'summary': self._generate_summary(analysis_data),
            'technical': analysis_data.get('smc_analysis', {}),
            'recommendation': self._generate_recommendation(analysis_data),
            'risk_assessment': self._assess_risk(analysis_data)
        }
    
    def _generate_summary(self, data):
        price = data.get('price', 0)
        smc = data.get('smc_analysis', {})
        bias = smc.get('bias', 'NEUTRAL')
        session = smc.get('session', 'UNKNOWN')
        return f"سعر {price:.2f} | اتجاه {bias} | جلسة {session}"
    
    def _generate_recommendation(self, data):
        smc = data.get('smc_analysis', {})
        bias = smc.get('bias', 'NEUTRAL')
        
        if bias == 'BULLISH':
            return "🔵 شراء مع اختراق المقاومة"
        elif bias == 'BEARISH':
            return "🔴 بيع مع كسر الدعم"
        return "⏳ الانتظار حتى وضوح الرؤية"
    
    def _assess_risk(self, data):
        risk_score = 0
        smc = data.get('smc_analysis', {})
        
        if smc.get('structure') == 'CONSOLIDATION':
            risk_score += 20
        if smc.get('session') == 'OFF_SESSION':
            risk_score += 15
        
        risk_level = 'منخفضة' if risk_score < 30 else 'متوسطة' if risk_score < 60 else 'مرتفعة'
        return {
            'score': risk_score,
            'level': risk_level,
            'description': f"مخاطر {risk_level} ({risk_score}%)"
        }
