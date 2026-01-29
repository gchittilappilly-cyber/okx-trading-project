import asyncio
import json
import websockets
import ssl, certifi # certifi is a Python package that contains a current, verified list
#                     of trusted Certificate Authorities (CAs) - the same ones browsers use.
#                     When Python’s built-in SSL verifier doesn’t trust a certificate, certifi
#                     provides an updated CA list to fix that.
import sys

OKX_WS_URL = "wss://wspap.okx.com:443/ws/v5/public?brokerId=9999"

ssl_context = ssl.create_default_context(cafile=certifi.where()) # ssl.create_default_context() creates a standard
#                                                                  TLS client context (object which controls certif-
#                                                                  icate verification, allowed protocols, ciphers, etc
#                                                                * By default, it would use your system or Python's
#                                                                * internal CA bundle - which might be incomplete.
#                                                                * By adding cafile=certifi.where(), we explicitly tell
#                                                                  it: "Use the trusted CA certificates from certifi
#                                                                  instead."
#                                                                * So now, when Python performs the TLS handshake, it
#                                                                  checks the OKX server’s certificate against
#                                                                  certifi’s root CA list.
#                                                                * Since OKX’s certificate chain is valid (just not
#                                                                  in your older default bundle), the handshake now
#                                                                  succeeds.

# Public channels for BTC/USD
SUBSCRIPTIONS = [
    {"op": "subscribe", "args": [{"channel": "tickers", "instId": "BTC-USD"}]}
]


async def heartbeat(ws):
    """Send a ping every 20 seconds to keep the connection alive."""
    while True:
        try:
            await ws.send("ping")
            await asyncio.sleep(20)
        except Exception as e:
            print("Heartbeat stopped:", e)
            break


async def print_prices(latest_data):
    """Print best bid/ask on one continuously updating line."""
    while True:
        askPx = latest_data.get("askPx", "N/A")
        askSz = latest_data.get("askSz", "N/A")
        bidPx = latest_data.get("bidPx", "N/A")
        bidSz = latest_data.get("bidSz", "N/A")

        # '\r' returns cursor to start of the line; end='' prevents newline
        # flush=True ensures it shows immediately
        sys.stdout.write(
            f"\raskPx: {askPx}, askSz: {askSz}, bidPx: {bidPx}, bidSz: {bidSz} 😭✌️🥀"
        )
        sys.stdout.flush()

        await asyncio.sleep(1)


async def main():
    latest_data = {}

    async with websockets.connect(OKX_WS_URL, ssl=ssl_context) as ws:
        # Send subscription
        for sub in SUBSCRIPTIONS:
            await ws.send(json.dumps(sub))
            print("Sent subscription:", json.dumps(sub))

        # Start background tasks
        asyncio.create_task(heartbeat(ws))
        asyncio.create_task(print_prices(latest_data))

        # Handle incoming messages
        async for msg in ws:
            msg = msg.strip()
            if msg in ("pong", ""):
                continue

            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                continue

            if "arg" in data and "data" in data:
                # Extract first (latest) tick
                tick = data["data"][0]
                latest_data["askPx"] = tick.get("askPx", "N/A")
                latest_data["askSz"] = tick.get("askSz", "N/A")
                latest_data["bidPx"] = tick.get("bidPx", "N/A")
                latest_data["bidSz"] = tick.get("bidSz", "N/A")

if __name__ == "__main__":
    asyncio.run(main())