# Project Docker / compose commands (pydaadop)

This file contains project-specific Docker and Docker Compose commands for building the app, running the API, and running tests using the `test-runner` service defined in [docker-compose.yml](docker-compose.yml).

See the compose file: [docker-compose.yml](docker-compose.yml)

**Build images**
- Build all images defined in `docker-compose.yml`:
  - `docker compose build`
- Build the main app image and test image explicitly:
  - `docker build -f Dockerfile -t pydaadop:dev .`
  - `docker build -f Dockerfile.test -t pydaadop:test .`

**Start core services**
- Start MongoDB and the app in detached mode:
  - `docker compose up -d mongo app`
- Check running services and follow logs:
  - `docker compose ps`
  - `docker compose logs -f app`

**Run the application (development)**
# Project Docker / compose commands (pydaadop)

This file contains project-specific Docker and Docker Compose commands for building the app, running the API, and running tests using the `test-runner` service defined in [docker-compose.yml](docker-compose.yml).

See the compose file: [docker-compose.yml](docker-compose.yml)

**Build images**
- Build all images defined in `docker-compose.yml`:
  - `docker compose build`
- Build the main app image and test image explicitly:
  - `docker build -f Dockerfile -t pydaadop:dev .`
  - `docker build -f Dockerfile.test -t pydaadop:test .`

**Start core services**
- Start MongoDB and the app in detached mode:
  - `docker compose up -d mongo app`
- Check running services and follow logs:
  - `docker compose ps`
  - `docker compose logs -f app`

**Run the application (development)**
- Start the `app` service (rebuild first if needed):
  - `docker compose up -d --build app`
- Open the OpenAPI docs in your browser at http://localhost:8002/docs (the compose file maps host port 8002 → container 8000).

**Run tests (test-runner service)**
The repository provides a `test-runner` service that uses `Dockerfile.test` and runs `./scripts/wait_and_test.sh` inside the compose network.

- Option A — start the `test-runner` via `up` (recommended; brings up dependencies automatically):
  - `docker compose up --build --exit-code-from test-runner test-runner`
  - This will build the images, start `mongo` and `app` as needed, run the test script, and exit with the runner's exit code.

- Option B — start dependencies first, then run the runner (explicit):
  - `docker compose up -d mongo app`
  - `docker compose run --rm test-runner`

Notes:
- `docker compose run` does not automatically start `depends_on` services — start `mongo` and `app` first when using `run`.

**One-off / maintenance commands**
- Rebuild and restart a single service (example `app`):
  - `docker compose up -d --build app`
- Stop and remove containers, networks, and anonymous volumes:
  - `docker compose down --volumes`
- Remove the built images (careful with local changes):
  - `docker image rm pydaadop:dev pydaadop:test`

**Environment files**
- The compose file reads environment from the repository's `.env` (and may reference `.env.docker`). Ensure variables like `MONGO_CONNECTION_STRING` are set appropriately for local dev or CI.

**Windows PowerShell tips**
- Inline environment variables for `docker run` on PowerShell:
  - `docker compose run --rm -e "MY_VAR=value" service`
- Use PowerShell to set a session env var before running compose:
  - `$env:MY_VAR = "value"; docker compose run --rm service`

**Troubleshooting**
- If tests hang or fail due to the app not being available, ensure `app` and `mongo` are reachable on the compose network (start them with `docker compose up -d mongo app`).
- If `wait_and_test.sh` fails, make sure it is executable and that repo files are mounted/readable by the `test-runner` service.

If you want, I can add small helper scripts (PowerShell and bash) under `.agents/scripts/` to wrap the most common command sequences (start, test, clean). Would you like me to add those?
