from typing import Callable

import micropip

decrypt_dependencies_installed: bool = False
_get_data: Callable[[], str] | None = None


async def install_client_dependencies() -> None:
    await micropip.install(
        "https://raw.githubusercontent.com/psymbio/pyodide_wheels/main/multidict/multidict-4.7.6-py3-none-any.whl",
        keep_going=True,
    )
    await micropip.install(
        "https://raw.githubusercontent.com/psymbio/pyodide_wheels/main/frozenlist/frozenlist-1.4.0-py3-none-any.whl",
        keep_going=True,
    )
    await micropip.install(
        "https://raw.githubusercontent.com/psymbio/pyodide_wheels/main/aiohttp/aiohttp-4.0.0a2.dev0-py3-none-any.whl",
        keep_going=True,
    )
    await micropip.install(
        "https://raw.githubusercontent.com/psymbio/pyodide_wheels/main/openai/openai-1.3.7-py3-none-any.whl",
        keep_going=True,
    )
    await micropip.install(
        "https://raw.githubusercontent.com/psymbio/pyodide_wheels/main/urllib3/urllib3-2.1.0-py3-none-any.whl",
        keep_going=True,
    )
    await micropip.install("ssl")

    await micropip.install("httpx", keep_going=True)
    await micropip.install(
        "https://raw.githubusercontent.com/psymbio/pyodide_wheels/main/urllib3/urllib3-2.1.0-py3-none-any.whl",
        keep_going=True,
    )


async def install_decrypt_dependencies_and_get_data() -> Callable[[], str]:
    global decrypt_dependencies_installed, _get_data

    if decrypt_dependencies_installed and _get_data is not None:
        return _get_data

    decrypt_dependencies_installed = True
    await micropip.install("cryptography==42.0.5")

    from decrypt import get_data as get_data

    _get_data = get_data
    return _get_data
