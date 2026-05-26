"use client";

import { useState } from "react";
import { Link2 } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export function UrlAnalyzer({
  locale,
  onUrlValidated,
}: {
  locale: string;
  onUrlValidated: (result: any) => void;
}) {
  const zh = locale === "zh";
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze() {
    if (!url.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const resp = await fetch(`${API}/discovery/analyze-url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });
      const json = await resp.json();
      setResult(json);
      onUrlValidated(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-3">
      <div>
        <label className="mb-1.5 block text-sm font-semibold text-ink">
          {zh ? "官方项目链接" : "Official Program URL"}
        </label>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://..."
          className="w-full rounded-xl border border-line bg-white px-3 py-2.5 text-sm"
          onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
        />
      </div>

      <button
        onClick={handleAnalyze}
        disabled={loading || !url.trim()}
        className="inline-flex items-center gap-2 rounded-xl border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink transition hover:bg-gray-50 disabled:opacity-50"
      >
        <Link2 size={16} />
        {loading ? (zh ? "分析中..." : "Analyzing...") : zh ? "分析链接" : "Analyze Link"}
      </button>

      {error && <p className="text-sm text-rose-600">{error}</p>}

      {result && (
        <div
          className={`rounded-xl border p-3 text-sm ${
            result.validation?.is_official
              ? "border-emerald-200 bg-emerald-50 text-emerald-800"
              : "border-amber-200 bg-amber-50 text-amber-800"
          }`}
        >
          {result.validation?.is_official
            ? zh
              ? "该链接匹配官方来源。"
              : "This URL matches an official source."
            : result.validation?.message || (zh ? "该链接不匹配任何已知官方来源。" : "This URL does not match any known official source.")}
        </div>
      )}
    </div>
  );
}
