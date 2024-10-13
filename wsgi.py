# wsgi.py
import logging
from app.server import app

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    logging.info('Starting...')
    app.run()