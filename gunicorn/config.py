import multiprocessing
import os

timeout = 5
bind = "[::]:" + os.environ.get("GUNICORN_PORT", "8888")

logconfig = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.ini")
worker_class = "aiohttp.GunicornWebWorker"
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
