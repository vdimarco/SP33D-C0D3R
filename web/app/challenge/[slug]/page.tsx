"use client";
import { useEffect, useRef, useState } from "react";
import Editor from "@monaco-editor/react";

export default function ChallengePage({ params }: { params: { slug: string } }) {
  const [prompt, setPrompt] = useState<string>("");
  const [code, setCode] = useState<string>("");
  const [runId, setRunId] = useState<string>("");
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [timer, setTimer] = useState<number>(0);
  const [logs, setLogs] = useState<string>("");
  const pasteCharsRef = useRef<number>(0);

  useEffect(() => {
    (async () => {
      const me = await fetch("/api/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ handle: "anon" })
      }).then(r => r.json());
      const p = await fetch(`/api/challenges/${params.slug}`).then(r => r.json());
      setPrompt(p.prompt);
      setCode(p.starter);
      const run = await fetch("/api/runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: me.id, challenge_slug: params.slug })
      }).then(r => r.json());
      setRunId(run.run_id);
      setStartedAt(Date.now());
    })();
  }, [params.slug]);

  useEffect(() => {
    if (!startedAt) return;
    const id = setInterval(() => setTimer(Date.now() - startedAt), 100);
    return () => clearInterval(id);
  }, [startedAt]);

  function onEditorMount(editor: any) {
    editor.onDidPaste((e: any) => {
      const chars = e.range.endColumn - e.range.startColumn;
      pasteCharsRef.current += Math.max(chars, 0);
      fetch(`/api/runs/${runId}/assist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chars })
      }).catch(() => {});
    });
  }

  async function onRun() {
    await fetch(`/api/runs/${runId}/attempt`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code })
    });
    const res = await fetch(`/api/runs/${runId}/tail`).then(r => r.json());
    setLogs((res.logs?.public || "") + "\n" + (res.passed ? "ALL TESTS GREEN" : ""));
    if (res.passed) alert("🎉 Passed! Time: " + (timer / 1000).toFixed(2) + "s");
  }

  return (
    <div className="p-6 grid grid-cols-2 gap-6">
      <div>
        <h1 className="text-2xl font-semibold mb-2">{params.slug}</h1>
        <p className="mb-4 whitespace-pre-wrap">{prompt}</p>
        <div className="text-sm opacity-70 mb-2">Time: {(timer / 1000).toFixed(2)}s</div>
        <Editor
          height="60vh"
          defaultLanguage="python"
          value={code}
          onChange={v => setCode(v || "")}
          onMount={onEditorMount}
          options={{ fontSize: 14, minimap: { enabled: false } }}
        />
        <button onClick={onRun} className="mt-3 px-4 py-2 rounded bg-black text-white">
          Run tests
        </button>
      </div>
      <pre className="bg-neutral-100 p-4 rounded overflow-auto h-[75vh]">{logs || "Logs..."}</pre>
    </div>
  );
}
