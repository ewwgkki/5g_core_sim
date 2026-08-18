# amf/session.py
# Shared in-memory store for pending GMLC positioning sessions
# Keyed by lcsCorrelationId

import asyncio

# {
#   lcsCorrelationId: {
#       "event":            asyncio.Event,
#       "result":           dict | None,
#       "ueContextId":      str,
#       "lmf_callback_uri": str,   # LMF's N1MessageNotify callback URI
#   }
# }
pending: dict[str, dict] = {}
