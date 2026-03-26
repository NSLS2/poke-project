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
| `BACKEND_INTERFACE` | `127.0.0.1` | IP address of the network interface the backend binds to |
| `BACKEND_PORT` | `8000` | Port for the FastAPI backend server |
| `BACKEND_HOSTNAME` | `localhost` | Hostname the frontend proxy uses to reach the backend |
| `FRONTEND_INTERFACE` | `127.0.0.1` | IP address of the network interface the frontend binds to |
| `FRONTEND_PORT` | `8080` | Port for the Vite frontend dev server |

For example, to run on different ports:

```xonsh
$BACKEND_PORT = "9000"
$FRONTEND_PORT = "9090"
pixi run app
```

To bind to all interfaces (e.g. for access from other machines):

```xonsh
$BACKEND_INTERFACE = "0.0.0.0"
$FRONTEND_INTERFACE = "0.0.0.0"
pixi run app
```

To bind the backend to a specific interface while having the proxy
reach it by a different name:

```xonsh
$BACKEND_INTERFACE = "192.168.1.10"
$BACKEND_HOSTNAME = "my-backend.local"
pixi run app
```
