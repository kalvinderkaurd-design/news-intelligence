# Gunicorn configuration file for professional production deployment
import multiprocessing
import os

bind = "0.0.0.0:" + os.environ.get("PORT", "5000")
workers = 1
threads = 8
timeout = 120
worker_class = "gthread"
