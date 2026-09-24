#!/usr/bin/env python3
"""Compatibility entry point for the standalone dashboard backend."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dashboard.server import Dashboard, ThreadingHTTPServer, make_handler, main

if __name__ == '__main__':
    main()
