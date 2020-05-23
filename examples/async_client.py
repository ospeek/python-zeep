import asyncio
import httpx
import time

import zeep

from zeep.asyncio import AsyncTransport


import logging.config

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep': {
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})


async def run_full_async():
    print("async example")
    print("=============")

    result = []

    def handle_future(future):
        result.extend(future.result())

    async with httpx.AsyncClient() as httpx_client:
        transport = AsyncTransport(cache=None, client=httpx_client)
        client = zeep.AsyncClient(transport=transport)

        await client.load_wsdl("https://public-dis-stage.dpd.nl/Services/ParcelShopFinderService.svc?wsdl")

        st = time.time()
        result = await client.service.slow_request("request-1")  # takes 1 sec
        print("time: %.2f" % (time.time() - st))


def run_async():
    print("async example")
    print("=============")

    result = []

    def handle_future(future):
        result.extend(future.result())

    loop = asyncio.get_event_loop()

    transport = AsyncTransport(loop, cache=None)
    client = zeep.Client("http://localhost:8000/?wsdl", transport=transport)

    tasks = [
        client.service.slow_request("request-1"),  # takes 1 sec
        client.service.slow_request("request-2"),  # takes 1 sec
    ]
    future = asyncio.gather(*tasks, return_exceptions=True)

    result = []
    future.add_done_callback(handle_future)

    st = time.time()
    loop.run_until_complete(future)
    loop.run_until_complete(transport.session.close())
    print("time: %.2f" % (time.time() - st))
    print("result: %s", result)
    print("")
    return result


def run_sync():
    print("sync example")
    print("============")
    transport = zeep.Transport(cache=None)
    client = zeep.Client("http://localhost:8000/?wsdl", transport=transport)

    st = time.time()
    result = [
        client.service.slow_request("request-1"),  # takes 1 sec
        client.service.slow_request("request-2"),  # takes 1 sec
    ]
    print("Time: %.2f" % (time.time() - st))
    print("result: %s", result)
    print("\n")

    return result


if __name__ == "__main__":
    print("")
    asyncio.run(run_full_async())
    # run_async()
    # run_sync()
