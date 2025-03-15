import asyncio

import flet as ft

from core import configure_core, sender

api_key: str = ""


async def async_app(page: ft.Page) -> None:
    # Set the browser's title bar text
    page.title = "Pyodide Chat GPT"

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.colors.BLUE,
            on_primary=ft.colors.WHITE,
            secondary=ft.colors.BLUE_500,
            on_secondary=ft.colors.WHITE,
            background=ft.colors.BLUE_50,
            surface=ft.colors.BLUE_100,
            on_surface=ft.colors.BLUE_900,
        )
    )

    messages: list[str] = []

    async def send_message(e) -> None:
        if not message_input.value:
            return
        messages.append(f"You: {message_input.value}")
        await sender(api_key, message_input.value)
        message_input.value = ""
        await update_messages_display()
        # Set focus back to the message input
        message_input.focus()

    async def update_messages_display() -> None:
        chat_display.value = "\n".join(messages)
        chat_display.update()

    async def callback(message: str | None) -> None:
        messages.append(f"AI: {message}")
        await update_messages_display()

    async def submit_api_key(e) -> None:
        global api_key
        if api_key_input.value is not None:
            api_key = api_key_input.value
        page.close(api_key_dialog)

    chat_display: ft.TextField = ft.TextField(
        read_only=True,
        multiline=True,
        filled=True,
        expand=False,
    )
    chat_display.height = 300  # Set fixed height
    chat_display.width = 400  # Set fixed width

    message_input: ft.TextField = ft.TextField(
        label="Your Message",
        autofocus=True,
        on_submit=send_message,
        filled=True,
    )

    send_button: ft.TextButton = ft.TextButton(
        text="Send",
        icon=ft.icons.SEND,
        on_click=send_message,
        style=ft.ButtonStyle(bgcolor=ft.colors.BLUE, color=ft.colors.WHITE),
    )

    api_key_input: ft.TextField = ft.TextField(
        label="OpenAI API Key (press Enter to skip)",
        autofocus=True,
        on_submit=submit_api_key,
        filled=True,
    )

    api_key_dialog: ft.AlertDialog = ft.AlertDialog(
        title=ft.Text("OpenAI API Key"),
        modal=True,
        content=api_key_input,
        actions=[ft.TextButton("Submit", on_click=submit_api_key)],
    )

    page.add(
        ft.Column(
            controls=[
                ft.Text(
                    "Pyodide Chat GPT",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLACK,
                ),
                chat_display,
                ft.Row(
                    controls=[message_input, send_button],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,  # Centering the row
                ),
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Centering the column
            expand=True,
        )
    )

    page.open(api_key_dialog)

    await configure_core(callback)


loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
loop.run_until_complete(ft.app_async(async_app))
