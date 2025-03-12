import asyncio
import json
import ssl
from urllib.parse import quote_plus

import httpx
import openai
from pyodide.ffi import create_proxy
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import js_module


class URLLib3Transport(httpx.BaseTransport):
    def __init__(self) -> None:
        self.pool = urllib3.PoolManager()

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8").replace("'", '"'))
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


client: httpx.Client = httpx.Client(transport=URLLib3Transport())
openai_client: openai.OpenAI = openai.OpenAI(
    base_url="https://api.openai.com/v1/", api_key="", http_client=client
)
message_queue: asyncio.Queue[tuple[str, str]] = asyncio.Queue()
loop: asyncio.AbstractEventLoop | None = None


async def handle_message(api_key: str, message: str) -> None:
    # Interactive with the OpenAI API
    openai_client.api_key = api_key
    response = openai_client.chat.completions.create(
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
    js_module.displayResponse(response.choices[0].message.content)


async def receiver() -> None:
    while True:
        api_key, message = await message_queue.get()
        await handle_message(api_key, message)


def sender(api_key: str, message: str) -> None:
    message_queue.put_nowait((api_key, message))


async def main() -> None:
    global loop

    loop = asyncio.get_running_loop()
    loop.create_task(receiver())
    while True:
        await asyncio.sleep(0.1)


sender_message_proxy = create_proxy(sender)
