from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2, os, docker, json

app = FastAPI()
dclient = docker.from_env()

def db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

class NewUser(BaseModel):
    handle: str

class NewRun(BaseModel):
    user_id: str
    challenge_slug: str

class AssistEvt(BaseModel):
    chars: int

class Attempt(BaseModel):
    code: str

class RunResult(BaseModel):
    passed: bool
    public_ok: bool
    hidden_ok: bool
    logs: dict

@app.post("/users")
def create_user(u: NewUser):
    with db() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO users(handle) VALUES(%s) RETURNING id", (u.handle,))
        return {"id": cur.fetchone()[0]}

@app.post("/runs")
def create_run(r: NewRun):
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, language FROM challenges WHERE slug=%s", (r.challenge_slug,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "challenge not found")
        chal_id, lang = row
        cur.execute("""INSERT INTO runs(user_id, challenge_id, details) VALUES(%s,%s,%s) RETURNING id""",
                    (r.user_id, chal_id, json.dumps({})))
        run_id = cur.fetchone()[0]
    container = dclient.containers.run(
        image="sp33d-runner-python:latest",
        command=["/entrypoint.sh", run_id],
        detach=True,
        network_disabled=True,
        mem_limit="512m",
        volumes={
            os.path.abspath(f"./challenges/{r.challenge_slug}"): {"bind": "/challenge", "mode": "ro"}
        },
    )
    with db() as conn, conn.cursor() as cur:
        cur.execute("UPDATE runs SET details = details || %s::jsonb WHERE id=%s",
                    (json.dumps({"container_id": container.id}), run_id))
    return {"run_id": run_id, "container_id": container.id}

@app.post("/runs/{run_id}/assist")
def assist(run_id: str, evt: AssistEvt):
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            """
            UPDATE runs SET
              assist_paste_events = assist_paste_events + 1,
              assist_paste_chars = assist_paste_chars + %s
            WHERE id=%s
            """,
            (evt.chars, run_id),
        )
        cur.execute(
            """INSERT INTO events(run_id, kind, data) VALUES(%s,'assist_paste', %s::jsonb)""",
            (run_id, json.dumps({"chars": evt.chars})),
        )
    return {"ok": True}

@app.post("/runs/{run_id}/attempt")
def attempt(run_id: str, req: Attempt):
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT details FROM runs WHERE id=%s", (run_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "run not found")
        details = row[0]
        container_id = details.get("container_id")
        cur.execute("UPDATE runs SET attempts = attempts + 1 WHERE id=%s", (run_id,))
        cur.execute("INSERT INTO events(run_id, kind) VALUES(%s,'attempt')", (run_id,))
    if not container_id:
        raise HTTPException(500, "container missing")
    container = dclient.containers.get(container_id)
    import io, tarfile
    data = req.code.encode()
    tarstream = io.BytesIO()
    with tarfile.open(fileobj=tarstream, mode='w') as tar:
        info = tarfile.TarInfo(name="starter.py")
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    tarstream.seek(0)
    container.put_archive("/workspace/challenge", tarstream.getvalue())
    container.exec_run("touch /signals/attempt")
    return {"ok": True}

@app.post("/runs/{run_id}/result")
def result(run_id: str, res: RunResult):
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT started_at, passed FROM runs WHERE id=%s", (run_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "run not found")
        started_at, already = row
        if res.passed and not already:
            cur.execute(
                """
                UPDATE runs SET passed=true, finished_at=now(), wall_ms = EXTRACT(MILLISECONDS FROM now() - started_at), details = details || %s::jsonb WHERE id=%s
                """,
                (json.dumps({"logs": res.logs}), run_id),
            )
            cur.execute("INSERT INTO events(run_id, kind, data) VALUES(%s,'pass',%s::jsonb)", (run_id, json.dumps(res.dict())))
        else:
            cur.execute(
                "UPDATE runs SET details = details || %s::jsonb WHERE id=%s",
                (json.dumps({"logs": res.logs}), run_id),
            )
            cur.execute("INSERT INTO events(run_id, kind, data) VALUES(%s,'fail',%s::jsonb)", (run_id, json.dumps(res.dict())))
    return {"ok": True}

@app.get("/challenges/{slug}")
def get_challenge(slug: str):
    path = os.path.join("challenges", slug)
    try:
        with open(os.path.join(path, "prompt.md")) as f:
            prompt = f.read()
        with open(os.path.join(path, "starter.py")) as f:
            starter = f.read()
    except FileNotFoundError:
        raise HTTPException(404, "challenge not found")
    return {"prompt": prompt, "starter": starter}

@app.get("/runs/{run_id}/tail")
def tail(run_id: str):
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT passed, details FROM runs WHERE id=%s", (run_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "run not found")
        passed, details = row
    logs = details.get("logs", {})
    return {"passed": passed, "logs": logs}

@app.get("/leaderboard/{slug}")
def leaderboard(slug: str):
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT u.handle, r.wall_ms, r.attempts, r.assist_paste_events, r.assist_paste_chars
            FROM runs r
            JOIN users u ON u.id = r.user_id
            JOIN challenges c ON c.id = r.challenge_id
            WHERE c.slug=%s AND r.passed=true
            ORDER BY r.wall_ms ASC, r.attempts ASC
            LIMIT 20
            """,
            (slug,),
        )
        rows = cur.fetchall()
    out = [
        {
            "handle": h,
            "wall_ms": w,
            "attempts": a,
            "assist_paste_events": e,
            "assist_paste_chars": ch,
        }
        for h, w, a, e, ch in rows
    ]
    return {"results": out}
