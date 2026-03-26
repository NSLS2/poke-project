# Poké Project

A Pokédex-like web application for your Pokémon catching needs.

To start the application, run the following `pixi` command and visit http://localhost:8080 in your web browser.

```sh
pixi run app
```

## Configuration

The following environment variables can be used to configure the application:

| Variable | Default | Description |
|---|---|---|
| `BACKEND_PORT` | `8000` | Port for the FastAPI backend server |
| `FRONTEND_PORT` | `8080` | Port for the Vite frontend dev server |

For example, to run on different ports:

```xonsh
$BACKEND_PORT = "9000"
$FRONTEND_PORT = "9090"
pixi run app
```
