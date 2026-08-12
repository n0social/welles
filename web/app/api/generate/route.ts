import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const maxDuration = 300;

type Body = {
  apiUrl?: string;
  mode?: string;
  prompt?: string;
  maxNewTokens?: number;
};

const MODES = new Set(["Write", "Rewrite", "Continue"]);

function resolveApiUrl(candidate: string | undefined): string | null {
  const fromEnv = process.env.WELLES_API_URL?.trim();
  const raw = (candidate || fromEnv || "").trim().replace(/\/$/, "");
  if (!raw) return null;

  let url: URL;
  try {
    url = new URL(raw);
  } catch {
    return null;
  }

  if (url.protocol !== "https:" && url.protocol !== "http:") return null;

  const host = url.hostname.toLowerCase();
  const allowed =
    host === "localhost" ||
    host === "127.0.0.1" ||
    host.endsWith(".ngrok-free.app") ||
    host.endsWith(".ngrok.io") ||
    host.endsWith(".ngrok.app") ||
    host.endsWith(".modal.run") ||
    host.endsWith(".trycloudflare.com");

  return allowed ? raw : null;
}

export async function POST(req: NextRequest) {
  let body: Body;
  try {
    body = (await req.json()) as Body;
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const mode = body.mode && MODES.has(body.mode) ? body.mode : "Write";
  const prompt = (body.prompt || "").trim();
  const maxNewTokens = Math.min(2048, Math.max(256, Number(body.maxNewTokens) || 768));
  const apiUrl = resolveApiUrl(body.apiUrl);

  if (!prompt) {
    return NextResponse.json({ error: "Prompt is required" }, { status: 400 });
  }

  if (!apiUrl) {
    return NextResponse.json(
      {
        error:
          "Paste a valid Colab API URL (ngrok / Modal). Example: https://….ngrok-free.app",
      },
      { status: 400 },
    );
  }

  try {
    const res = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // ngrok free browser warning bypass for server-side calls
        "ngrok-skip-browser-warning": "1",
      },
      body: JSON.stringify({ mode, prompt, maxNewTokens }),
    });
    const data = (await res.json()) as { text?: string; detail?: string; error?: string };
    if (!res.ok) {
      throw new Error(data.error || data.detail || `Upstream ${res.status}`);
    }
    return NextResponse.json({ text: data.text || "" });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Generation failed";
    console.error("Welles generate error:", message);
    return NextResponse.json(
      {
        error:
          "Could not reach Colab. Is the notebook still running? Re-copy the ngrok URL if it changed.",
        detail: message,
      },
      { status: 502 },
    );
  }
}
