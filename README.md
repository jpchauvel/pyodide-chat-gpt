# Pyodide Chat GPT

A small proof of concept using
[pyodide](https://pyodide.org/en/latest/index.html) and
[OpenAI GPT](https://platform.openai.com/docs/guides/gpt) to create a static page
to interact with GPT 3.5 Turbo.

## Installation

To build the project you have to first make sure you have `make` installed.

```sh
make all
```

Then you have to serve the static contect using Python's `http.server`:

```sh
python3 -m http.server --directory build
```

Then open your browser and navigate to http://localhost:8000.
