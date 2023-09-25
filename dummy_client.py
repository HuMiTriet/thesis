import asyncio
import time
import aiohttp

PROXY_URL = "http://127.0.0.1:5001/"


async def main():
    async with aiohttp.ClientSession() as session:
        latencies = []

        for i in range(5000):
            start_time = time.time()

            async with session.get(
                "http://localhost:5007/",
                # proxy=PROXY_URL,
            ) as response:
                await response.text()

            end_time = time.time()
            latency = end_time - start_time
            latencies.append(latency)
            print(f"Iteration {i+1}: Latency = {latency:.4f} seconds")

        avg_latency = sum(latencies) / len(latencies)
        print(f"Average Latency: {avg_latency:.4f} seconds")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
