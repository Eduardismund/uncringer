from fivetran_connector_sdk import Connector
from fivetran_connector_sdk import Operations as op
from datetime import datetime

def schema(configuration: dict):
    return {
        "audio_data": {
            "primary_key": ["id"],
            "properties": {
                "id": {"type": "string"},
                "filename": {"type": "string"},
                "transcript": {"type": "string"},
                "cringe_score": {"type": "number"},
                "timestamp": {"type": "string"}
            }
        }
    }

def update(configuration: dict, state: dict):
    # Sample data
    yield op.upsert("audio_data", {
        "id": "1",
        "filename": "test.mp3",
        "transcript": "um, like, you know",
        "cringe_score": 7.5,
        "timestamp": datetime.now().isoformat()
    })
    
    yield op.checkpoint(state={})

connector = Connector(update=update, schema=schema)