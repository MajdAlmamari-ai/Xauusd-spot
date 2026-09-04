# data_layer/scheduler.py
import schedule
import threading
import time
import logging

logger = logging.getLogger(__name__)

class DataScheduler:
    """جدولة تلقائية"""
    
    def __init__(self, fetcher, callback):
        self.fetcher = fetcher
        self.callback = callback
        self.running = False
    
    def start(self):
        self.running = True
        schedule.every(5).minutes.do(self._fetch_and_process)
        thread = threading.Thread(target=self._run_schedule)
        thread.daemon = True
        thread.start()
        logger.info("✅ بدء الجدولة")
    
    def _run_schedule(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def _fetch_and_process(self):
        df = self.fetcher.fetch()
        if df is not None and not df.empty:
            self.callback(df)
    
    def stop(self):
        self.running = False
