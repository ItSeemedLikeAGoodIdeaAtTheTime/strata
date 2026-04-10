"""
Vercel serverless entry point for Strata.
Routes all requests to the FastAPI app.
"""
import os

# Vercel's only writable directory
os.environ.setdefault("STRATA_DATA_DIR", "/tmp")

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strata import app
