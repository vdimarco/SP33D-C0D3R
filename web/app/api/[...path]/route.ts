import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

async function handler(req: NextRequest, { params }: { params: { path: string[] } }) {
  const url = `${API_BASE}/${params.path.join("/")}${req.nextUrl.search}`;
  const init: RequestInit = {
    method: req.method,
    headers: req.headers as any,
    body: req.method !== "GET" && req.method !== "HEAD" ? await req.text() : undefined,
  };
  const resp = await fetch(url, init);
  const body = await resp.text();
  return new NextResponse(body, { status: resp.status, headers: resp.headers });
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const DELETE = handler;
