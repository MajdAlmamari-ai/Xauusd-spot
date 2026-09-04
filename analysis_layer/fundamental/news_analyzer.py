# analysis_layer/fundamental/news_analyzer.py
import logging

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """تحليل الأخبار الاقتصادية"""
    
    def __init__(self):
        self.impact_keywords = {
            'HIGH': ['CPI', 'interest rate', 'FOMC', 'Nonfarm', 'GDP', 'inflation'],
            'MEDIUM': ['jobs', 'unemployment', 'retail sales', 'consumer confidence'],
            'LOW': ['speech', 'forecast', 'meeting', 'statement']
        }
    
    def analyze(self, news_list):
        if not news_list:
            return {'impact': 'LOW', 'sentiment': 0, 'key_events': []}
        
        analysis = {
            'impact': 'LOW',
            'sentiment': 0,
            'key_events': [],
            'summary': 'لا توجد أخبار ذات تأثير'
        }
        
        for news in news_list[:10]:
            title = news.get('title', '')
            description = news.get('description', '')
            combined = (title + ' ' + description).upper()
            
            impact_score = 0
            for level, keywords in self.impact_keywords.items():
                for keyword in keywords:
                    if keyword.upper() in combined:
                        impact_score += {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}[level]
            
            if impact_score >= 5:
                analysis['impact'] = 'HIGH'
                analysis['key_events'].append({
                    'title': title[:50],
                    'impact': impact_score
                })
            elif impact_score >= 2 and analysis['impact'] != 'HIGH':
                analysis['impact'] = 'MEDIUM'
        
        return analysis
