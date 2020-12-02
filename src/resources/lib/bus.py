import asyncio
import ravel
import threading

BUS = ravel.system_bus()
_LOOP = asyncio.get_event_loop()

BUS.attach_asyncio(_LOOP)
threading.Thread(target=_LOOP.run_forever, daemon=True).start()
