## Define message format and serialization methods
import json

def encode_message(message: dict) -> bytes:
    return json.dumps(message).encode('utf-8')

def decode_message(message: bytes) -> dict:
    return json.loads(message.decode('utf-8'))