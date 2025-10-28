import asyncio
import json
import websockets

OKX_WS_URL = "wss://wspap.okx.com:443/ws/v5/public?brokerId=9999"

# Public channels for BTC/USD (spot and swap)
SUBSCRIPTIONS = [
    {"op": "subscribe", "args": [{"channel": "tickers", "instId": "BTC-USD"}]}  # Swap
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

async def main():
    async with websockets.connect(OKX_WS_URL) as ws:
        # Subscribe to tickers
        for sub in SUBSCRIPTIONS:
            await ws.send(json.dumps(sub))
            print("Sent subscription:", json.dumps(sub))

        # Start heartbeat
        asyncio.create_task(heartbeat(ws))

        # Read messages
        async for msg in ws:
            msg = msg.strip()
            if msg == "pong" or msg == "":
                print("(pong)")
                continue

            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                print("Non-JSON message:", msg)
                continue

            if "event" in data:
                print("Event:", data)
            elif "arg" in data and "data" in data:
                print("jsonObj:", data)
            else:
                print("Other:", data)

if __name__ == "__main__":
    asyncio.run(main())