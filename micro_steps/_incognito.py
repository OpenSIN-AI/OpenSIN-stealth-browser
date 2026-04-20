import os
import nodriver as uc

PORT_FILE = "/tmp/incognito_port.txt"


def _incognito_port():
    if os.path.exists(PORT_FILE):
        try:
            return int(open(PORT_FILE).read().strip())
        except Exception:
            pass
    return 9335


async def attach_incognito():
    port = _incognito_port()
    b = await uc.start.__wrapped__(host="127.0.0.1", port=port)
    b._browser_process = None
    b._process_pid = None
    return b
