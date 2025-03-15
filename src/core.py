import asyncio
import json
from typing import Awaitable, Callable
from urllib.parse import quote_plus

from install_dependencies import (install_client_dependencies,
                                  install_decrypt_dependencies_and_get_data)

app_api_key: str | None = None
message_queue: asyncio.Queue[tuple[str, str]] = asyncio.Queue()


async def get_api_key(user_api_key: str) -> str:
    global app_api_key

    get_data: Callable[[], str] = (
        await install_decrypt_dependencies_and_get_data()
    )

    if user_api_key != "":
        return user_api_key
    if app_api_key is None:
        app_api_key = get_data()
        return app_api_key
    return app_api_key


async def handle_message(
    openai_client,
    api_key: str,
    message: str,
    callback: Callable[[str | None], Awaitable[None]],
) -> None:
    openai_client.api_key = await get_api_key(api_key)
    response = await openai_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": quote_plus(message),
            }
        ],
        model="gpt-3.5-turbo",
        max_tokens=4096,
        temperature=0.2,
    )
    await callback(response.choices[0].message.content)


async def receiver(
    openai_client, callback: Callable[[str | None], Awaitable[None]]
) -> None:
    while True:
        api_key, message = await message_queue.get()
        await handle_message(openai_client, api_key, message, callback)


async def sender(api_key: str, message: str) -> None:
    await message_queue.put((api_key, message))


async def configure_client():
    await install_client_dependencies()

    import ssl

    import httpx
    import openai
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    class URLLib3Transport(httpx.AsyncBaseTransport):
        def __init__(self) -> None:
            self.pool = urllib3.PoolManager()

        async def handle_async_request(
            self, request: httpx.Request
        ) -> httpx.Response:
            payload = json.loads(
                request.content.decode("utf-8").replace("'", '"')
            )
            urllib3_response = self.pool.request(
                request.method,
                str(request.url),
                headers=request.headers,
                json=payload,
            )  # Convert httpx.URL to string
            content = json.loads(
                urllib3_response.data.decode("utf-8")
            )  # Decode the data and load as JSON
            stream = httpx.ByteStream(
                json.dumps(content).encode("utf-8")
            )  # Convert back to JSON and encode
            headers = [(b"content-type", b"application/json")]
            return httpx.Response(200, headers=headers, stream=stream)

    client: httpx.AsyncClient = httpx.AsyncClient(transport=URLLib3Transport())
    openai_client = openai.AsyncOpenAI(
        base_url="https://api.openai.com/v1/", api_key="", http_client=client
    )
    return openai_client


async def configure_core(
    callback: Callable[[str | None], Awaitable[None]],
) -> None:
    openai_client = await configure_client()
    asyncio.create_task(receiver(openai_client, callback))
