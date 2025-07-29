## Define message format and serialization methods
import json

def encode_message(message: dict) -> bytes:
    return json.dumps(message).encode('utf-8')

def decode_message(message: bytes) -> dict:
    return json.loads(message.decode('utf-8'))

def decode_many(byte_data: bytes) -> list[dict]:
    ## Attempt to decode multiple JSON objects packed in a single TCP buffer.
    try:
        text = byte_data.decode('utf-8')
        messages = []
        while text:
            obj, index = json.JSONDecoder().raw_decode(text)
            messages.append(obj)
            text = text[index:].lstrip()
        return messages
    except json.JSONDecodeError:
        return []
