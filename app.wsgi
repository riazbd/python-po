import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/home/service_dreamdiver/projects/python-po")

from app import app as application