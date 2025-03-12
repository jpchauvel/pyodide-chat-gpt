async function setupPyodide() {
    const pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");

    // JavaScript functions to register with the Python environment
    const jsModule = {
        async displayResponse(response) {
            const chatbox = document.getElementById("chatbox");
            chatbox.innerHTML += `<div><strong>AI:</strong> ${response}</div>`;
        }
    };

    pyodide.registerJsModule("js_module", jsModule);

    await pyodide.runPythonAsync(`
        import micropip
        import os
        from pyodide.http import pyfetch

        response = await pyfetch("app.tar.gz")
        await response.unpack_archive()

        await micropip.install('https://raw.githubusercontent.com/psymbio/pyodide_wheels/main/multidict/multidict-4.7.6-py3-none-any.whl', keep_going=True)
        await micropip.install('https://raw.githubusercontent.com/psymbio/pyodide_wheels/main/frozenlist/frozenlist-1.4.0-py3-none-any.whl', keep_going=True)
        await micropip.install('https://raw.githubusercontent.com/psymbio/pyodide_wheels/main/aiohttp/aiohttp-4.0.0a2.dev0-py3-none-any.whl', keep_going=True)
        await micropip.install('https://raw.githubusercontent.com/psymbio/pyodide_wheels/main/openai/openai-1.3.7-py3-none-any.whl', keep_going=True)
        await micropip.install('https://raw.githubusercontent.com/psymbio/pyodide_wheels/main/urllib3/urllib3-2.1.0-py3-none-any.whl', keep_going=True)
        await micropip.install("ssl")
        import ssl
        await micropip.install("httpx", keep_going=True)
        import httpx
        await micropip.install('https://raw.githubusercontent.com/psymbio/pyodide_wheels/main/urllib3/urllib3-2.1.0-py3-none-any.whl', keep_going=True)
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        from main import sender_message_proxy
    `);
    
    // Prompt the user for the OpenAI API key
    const apiKey = window.prompt("Please enter your OpenAI API key:");

    // Add the HTML content after Pyodide setup.
    document.body.innerHTML += `
        <h1>Pyodide Chat with AI Assistant</h1>
        <div id="chatbox"></div>
        <input type="text" id="user-input" placeholder="Type your message...">
        <button id="send-button">Send</button>
    `;

    const sendMessageToPython = pyodide.globals.get("sender_message_proxy");

    // Add event listener to send button
    document.getElementById("send-button").addEventListener("click", () => {
        const userInput = document.getElementById("user-input").value;
        document.getElementById("user-input").value = "";
        const chatbox = document.getElementById("chatbox");
        chatbox.innerHTML += `<div><strong>You:</strong> ${userInput}</div>`;

        sendMessageToPython(apiKey, userInput);
    });

    // Add event listener for the Enter key on the input field
    document.getElementById("user-input").addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            document.getElementById("send-button").click();
        }
    });

    await pyodide.runPythonAsync(`
        from main import main as py_main

        await py_main()
    `);
}

document.addEventListener("DOMContentLoaded", function() {
    setupPyodide();
});
