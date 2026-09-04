# data_layer/scraping/monitor.py
import logging

logger = logging.getLogger(__name__)

class ScrapingMonitor:
    def __init__(self):
        self.metrics = {'requests': 0, 'successes': 0, 'failures': 0}
    
    def log_request(self, success, error=None):
        self.metrics['requests'] += 1
        if success:
            self.metrics['successes'] += 1
        else:
            self.metrics['failures'] += 1
