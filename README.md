# SP33D C0D3R

SP33D C0D3R is a minimal viable product for a speed-oriented coding platform.
Players race to solve programming challenges in the browser while the backend measures time to green across public and hidden tests.

## Project layout

- `api/` – FastAPI service providing user, run and leaderboard endpoints.
- `runner/` – Dockerized language runners that execute public and hidden tests.
- `challenges/` – Challenge bundles with prompts, starter code and tests.
- `web/` – Next.js frontend with a Monaco editor and API proxy.
- `infra/` – Database schema and other infrastructure files.

## Development

1. **Build the Python runner image**
   ```bash
   docker build -t sp33d-runner-python:latest runner/python
   ```
2. **Start the stack**
   ```bash
   docker compose up --build
   ```
3. **Seed a challenge** – insert at least one row into the `challenges` table (e.g. `fizzbuzz`).
4. Open `http://localhost:3000/challenge/fizzbuzz` in a browser to play.

## Testing

Challenges ship with public tests to verify starter implementations. For example:
```bash
(cd challenges/fizzbuzz && PYTHONPATH=. pytest tests_public)
```

---

Licensed under the MIT License. See `LICENSE` for details.
