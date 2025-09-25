import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fivetran_connector_sdk import Connector
from fivetran_connector import UncringerConnector

uncringer = UncringerConnector()
connector = Connector(update=uncringer.update, schema=uncringer.schema)