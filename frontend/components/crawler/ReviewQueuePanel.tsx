"use client";

import { useEffect, useState } from "react";
import { Badge } from "../common/Badge";
import { Button } from "../common/Button";
import { Card } from "../common/Card";

const API = "http://127.0.0.1:8000/api";

export function ReviewQueuePanel({ locale }: { locale: string }) {
  const zh = locale === "zh";
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API}/programs/review-queue`);
      const json = await response.json();
      if (!response.ok) throw new Error(JSON.stringify(json));
      setItems(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  async function review(id: number, review_status: string) {
    setError(null);
    try {
      const response = await fetch(`${API}/programs/${id}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ review_status }),
      });
      const json = await response.json();
      if (!response.ok) throw new Error(JSON.stringify(json));
      setItems((current) => current.filter((item) => item.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <Card className="p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="font-semibold">{zh ? "项目审核队列" : "Program Review Queue"}</h3>
          <p className="mt-2 text-sm text-muted">{zh ? "审核自动抽取项目。AI 推荐默认只使用已审核或高置信项目。" : "Review auto-extracted programs. Recommendations use reviewed or high-confidence programs by default."}</p>
        </div>
        <Button disabled={loading} onClick={load}>{zh ? "刷新" : "Refresh"}</Button>
      </div>
      {error && <p className="mt-3 text-sm text-rose-700">{error}</p>}
      <div className="mt-4 space-y-3">
        {items.length === 0 && <p className="text-sm text-muted">{zh ? "暂无待审核项目。" : "No programs waiting for review."}</p>}
        {items.slice(0, 10).map((item) => (
          <div key={item.id} className="rounded-2xl border border-line bg-gray-50 p-4">
            <div className="flex flex-col justify-between gap-3 md:flex-row md:items-start">
              <div>
                <div className="font-semibold">{item.program_name}</div>
                <p className="mt-1 text-xs text-muted">{item.university_name} · {item.field || "TBC"} · {item.source_url}</p>
                <p className="mt-2 line-clamp-3 text-xs text-muted">{item.raw_text_snapshot || item.description}</p>
              </div>
              <div className="flex flex-wrap gap-2 md:justify-end">
                <Badge tone={item.review_status === "needs_review" ? "warning" : "brand"}>{item.review_status}</Badge>
                <Badge tone="brand">{Math.round((item.extraction_confidence || 0) * 100)}%</Badge>
              </div>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <button onClick={() => review(item.id, "reviewed")} className="rounded-xl bg-emerald-600 px-3 py-2 text-xs font-semibold text-white">{zh ? "标记已审核" : "Mark reviewed"}</button>
              <button onClick={() => review(item.id, "rejected")} className="rounded-xl bg-rose-600 px-3 py-2 text-xs font-semibold text-white">{zh ? "拒绝" : "Reject"}</button>
              {item.source_url && <a href={item.source_url} target="_blank" className="rounded-xl border border-line bg-white px-3 py-2 text-xs font-semibold">{zh ? "打开官网" : "Open source"}</a>}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
