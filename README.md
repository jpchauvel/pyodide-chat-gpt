# Pyodide Chat GPT

A small proof of concept using
[pyodide](https://pyodide.org/en/latest/index.html) and
[OpenAI GPT](https://platform.openai.com/docs/guides/gpt) to create a static page
to interact with GPT 3.5 Turbo.

## Installation

To build the project you have to first make sure you have `poetry` installed.

```sh
poetry install --no-root
```

Then you have to build the app.

```sh
poetry run flet build web
```

Finally you have to run a python server to serve the app.

```sh
poetry run python -m http.server --directory build/web
```

Then open your browser and navigate to http://localhost:8000.
