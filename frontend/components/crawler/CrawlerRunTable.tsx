"use client";

import { useEffect, useState } from "react";
import { Card } from "../common/Card";

const API = "http://127.0.0.1:8000/api";

export function CrawlerRunTable({ locale }: { locale: string }) {
  const zh = locale === "zh";
  const [runs, setRuns] = useState<any[]>([]);
  const [rawPages, setRawPages] = useState<any[]>([]);
  const [extractions, setExtractions] = useState<any[]>([]);

  async function load() {
    const [runJson, rawJson, extractionJson] = await Promise.all([
      fetch(`${API}/crawler/runs`).then((r) => r.json()),
      fetch(`${API}/crawler/raw-pages`).then((r) => r.json()),
      fetch(`${API}/crawler/extraction-runs`).then((r) => r.json()),
    ]);
    setRuns(runJson);
    setRawPages(rawJson);
    setExtractions(extractionJson);
  }

  useEffect(() => {
    load().catch(() => undefined);
  }, []);

  const lastRun = runs[0];
  const stats = [
    [zh ? "来源总数" : "total sources", lastRun?.total_sources ?? 0],
    [zh ? "已抓页面" : "crawled pages", rawPages.length],
    [zh ? "抽取记录" : "extraction runs", extractions.length],
    [zh ? "失败页面" : "failed pages", lastRun?.failed_count ?? 0],
    [zh ? "robots 跳过" : "skipped by robots", lastRun?.skipped_count ?? 0],
    [zh ? "待审核" : "needs review", extractions.filter((item) => item.confidence < 0.75).length],
  ];
  return (
    <Card className="p-5">
      <div className="flex items-center justify-between gap-3">
        <h3 className="font-semibold">{zh ? "运行概览" : "Run Overview"}</h3>
        <button onClick={load} className="rounded-xl border border-line px-3 py-2 text-xs font-semibold">{zh ? "刷新" : "Refresh"}</button>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-3">{stats.map(([k, v]) => <div key={String(k)} className="rounded-xl bg-gray-50 p-4"><div className="text-2xl font-bold">{String(v)}</div><div className="text-sm text-muted">{String(k)}</div></div>)}</div>
      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <div><h4 className="font-semibold">{zh ? "原始页面" : "Raw Pages"}</h4><div className="mt-2 max-h-72 overflow-auto rounded-xl border border-line">{rawPages.slice(0, 8).map((page) => <div key={page.id} className="border-b border-line p-3 text-xs"><div className="font-semibold">{page.title || page.url}</div><div className="break-all text-muted">{page.url}</div></div>)}</div></div>
        <div><h4 className="font-semibold">{zh ? "抽取记录" : "Extraction Runs"}</h4><div className="mt-2 max-h-72 overflow-auto rounded-xl border border-line">{extractions.slice(0, 8).map((run) => <div key={run.id} className="border-b border-line p-3 text-xs"><div className="font-semibold">{run.status} · {Math.round((run.confidence || 0) * 100)}%</div><div className="text-muted">raw_page #{run.raw_page_id}</div></div>)}</div></div>
      </div>
    </Card>
  );
}
