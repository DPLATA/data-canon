import logging
from app.server import app

if __name__ == "__main__":
    logging.info('Starting...')
    app.run()