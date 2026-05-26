"use client";

import { useState } from "react";
import { Button } from "../common/Button";
import { Card } from "../common/Card";
import { ActionResult } from "../common/ActionResult";

function formatCrawlerResult(data: any, path: string, zh: boolean): string {
  if (!data) return "";
  if (path === "/crawler/seed-sources") {
    const u = data.universities ?? 0;
    const s = data.crawl_sources ?? 0;
    return zh
      ? `已写入 ${u} 所大学，${s} 个爬取源。`
      : `Seeded ${u} universities, ${s} crawl sources.`;
  }
  if (path === "/crawler/discover") {
    const total = data.total_candidates ?? 0;
    const success = data.success_count ?? 0;
    return zh
      ? `试运行完成：发现 ${total} 个候选链接，成功处理 ${success} 个来源。`
      : `Dry-run complete: ${total} candidate links found, ${success} sources processed.`;
  }
  if (path === "/crawler/fetch") {
    const fetched = (data.fetched_raw_page_ids || []).length;
    const success = data.success_count ?? 0;
    const skipped = data.skipped_count ?? 0;
    return zh
      ? `抓取完成：成功保存 ${fetched} 个页面，跳过 ${skipped} 个（受 robots 限制）。`
      : `Fetch complete: ${fetched} pages saved, ${skipped} skipped (robots).`;
  }
  if (path === "/crawler/extract") {
    const count = data.extracted_programs ?? 0;
    const ids = (data.program_ids || []).join(", ");
    const provider = data.provider === "mock" ? "Mock 规则" : data.provider;
    return zh
      ? `成功抽取 ${count} 个项目（ID: ${ids}），使用 ${provider} 提供者。`
      : `Extracted ${count} programs (ID: ${ids}), using ${provider} provider.`;
  }
  if (path === "/crawler/run-full-pipeline") {
    const fetched = (data.fetched_raw_page_ids || []).length;
    const success = data.success_count ?? 0;
    const skipped = data.skipped_count ?? 0;
    return zh
      ? `完整流程完成：成功抓取 ${fetched} 个页面（共 ${success} 次成功），跳过 ${skipped} 个。`
      : `Full pipeline complete: ${fetched} pages saved (${success} successes), ${skipped} skipped.`;
  }
  return "";
}

export function CrawlerControlPanel({ locale }: { locale: string }) {
  const zh = locale === "zh";
  const [loading, setLoading] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);

  const actions = [
    { label: zh ? "📋 种子入口" : "📋 Seed Sources", path: "/crawler/seed-sources", body: {} },
    { label: zh ? "🔍 发现链接" : "🔍 Discover Links", path: "/crawler/discover", body: { dry_run: true, max_pages_per_domain: 10 } },
    { label: zh ? "📥 抓取页面" : "📥 Fetch Pages", path: "/crawler/fetch", body: { dry_run: false, max_pages_per_domain: 10 } },
    { label: zh ? "🤖 抽取项目" : "🤖 Extract Programs", path: "/crawler/extract", body: { provider: "mock", limit: 10 } },
    { label: zh ? "🚀 完整流程" : "🚀 Full Pipeline", path: "/crawler/run-full-pipeline", body: { dry_run: true, max_pages_per_domain: 10 } },
  ];

  async function run(label: string, path: string, body: object) {
    setLoading(label);
    setError(null);
    setResult(null);
    setMessage(null);
    try {
      const response = await fetch(`http://127.0.0.1:8000/api${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const json = await response.json();
      if (!response.ok) throw new Error(JSON.stringify(json));
      setResult(json);
      setMessage(formatCrawlerResult(json, path, zh));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(null);
    }
  }

  return (
    <Card className="p-5">
      <h3 className="font-semibold">{zh ? "爬虫控制台" : "Crawler Control"}</h3>
      <p className="mt-1 text-sm text-muted">
        {zh
          ? "遵守 robots.txt 和速率限制；不登录、不绕过验证码、不付款、不最终提交。"
          : "Robots.txt, rate limits, no login, no CAPTCHA bypass, no payment, no final submit."}
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        {actions.map(({ label, path, body }) => (
          <Button
            disabled={loading !== null}
            key={label}
            onClick={() => run(label, path, body)}
          >
            {loading === label ? (zh ? "执行中..." : "Running...") : label}
          </Button>
        ))}
      </div>

      <ActionResult locale={locale} message={message} data={result} error={error} />
    </Card>
  );
}
