import asyncio
import json
import websockets
import ssl, certifi

OKX_WS_URL = "wss://wspap.okx.com:443/ws/v5/public?brokerId=9999"

# Public channels for BTC/USD
SUBSCRIPTIONS = [
    {"op": "subscribe", "args": [{"channel": "tickers", "instId": "BTC-USD"}]}
]

# imports a large list of certificates maintained my Mozilla to ensure that the correct certificate can be found
ssl_context = ssl.create_default_context(cafile=certifi.where())
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
    """Print best bid/ask every second."""
    while True:
        askPx = latest_data.get("askPx", "N/A")
        askSz = latest_data.get("askSz", "N/A")
        bidPx = latest_data.get("bidPx", "N/A")
        bidSz = latest_data.get("bidSz", "N/A")

        print(f"askPx: {askPx}, askSz: {askSz}, bidPx: {bidPx}, bidSz: {bidSz}")
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