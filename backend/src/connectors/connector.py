from fivetran_connector_sdk import Connector
from uncringer_fivetran import UncringerFivetranConnector

connector_instance = UncringerFivetranConnector()

connector = Connector(
    update=connector_instance.update,
    schema=connector_instance.schema
)