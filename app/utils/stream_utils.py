from __future__ import annotations

import json
from typing import Iterable

from flask import Response


def sse_message(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def build_sse_response(generator: Iterable[str]) -> Response:
    return Response(generator, mimetype="text/event-stream")

