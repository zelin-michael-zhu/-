"use client";

import { useState } from "react";
import { Search, Globe, Link2, Loader2 } from "lucide-react";
import { Card } from "@/components/common/Card";
import { RegionUniversitySelector } from "@/components/discovery/RegionUniversitySelector";
import { FieldSelector } from "@/components/discovery/FieldSelector";
import { UrlAnalyzer } from "@/components/discovery/UrlAnalyzer";
import { ProgressTimeline } from "@/components/discovery/ProgressTimeline";
import { ProgramResultCard } from "@/components/discovery/ProgramResultCard";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function ProgramDiscoveryClient({ locale }: { locale: string }) {
  const zh = locale === "zh";

  const [universityId, setUniversityId] = useState<number | null>(null);
  const [field, setField] = useState<string | null>(null);
  const [urlValidation, setUrlValidation] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleFindPrograms() {
    if (!universityId) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const resp = await fetch(`${API}/discovery/find-programs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          university_id: universityId,
          field: field,
          engine: "native_static",
          max_pages: 10,
        }),
      });
      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Request failed");
      }
      const json = await resp.json();
      setResult(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleFindFromUrl() {
    if (!urlValidation?.validation?.is_official) return;
    const url = urlValidation.url;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const resp = await fetch(`${API}/discovery/find-programs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: url,
          field: field,
          engine: "native_static",
          max_pages: 5,
        }),
      });
      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Request failed");
      }
      const json = await resp.json();
      setResult(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  const canFindFromUrl = urlValidation?.validation?.is_official;
  const programs = result?.programs || [];
  const steps = result?.steps || [];
  const summary = result?.progress_summary;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-ink">
          {zh ? "项目发现" : "Program Discovery"}
        </h1>
        <p className="mt-1 text-sm text-muted">
          {zh
            ? "从学校官网查找硕士项目，并自动整理成结构化申请信息。"
            : "Find official master's programs from university websites and turn them into structured application data."}
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Card A: Guided Search */}
        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2">
            <Search size={20} className="text-brand" />
            <h2 className="font-semibold text-ink">
              {zh ? "按地区和学校查找" : "Find by Region and University"}
            </h2>
          </div>

          <RegionUniversitySelector locale={locale} onUniversityChange={setUniversityId} />

          <div className="mt-4">
            <FieldSelector locale={locale} onFieldChange={setField} />
          </div>

          <button
            onClick={handleFindPrograms}
            disabled={!universityId || loading}
            className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-brand px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:bg-gray-300"
          >
            {loading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                {zh ? "搜索中..." : "Searching..."}
              </>
            ) : (
              <>
                <Search size={16} />
                {zh ? "查找官方项目" : "Find Official Programs"}
              </>
            )}
          </button>
        </Card>

        {/* Card B: URL Analysis */}
        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2">
            <Link2 size={20} className="text-brand" />
            <h2 className="font-semibold text-ink">
              {zh ? "分析官方链接" : "Analyze Official Link"}
            </h2>
          </div>

          <UrlAnalyzer locale={locale} onUrlValidated={setUrlValidation} />

          {canFindFromUrl && (
            <button
              onClick={handleFindFromUrl}
              disabled={loading}
              className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-brand px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:bg-gray-300"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  {zh ? "抓取中..." : "Fetching..."}
                </>
              ) : (
                <>
                  <Globe size={16} />
                  {zh ? "抓取并抽取项目" : "Fetch and Extract Programs"}
                </>
              )}
            </button>
          )}
        </Card>
      </div>

      {error && (
        <Card className="border-rose-200 bg-rose-50 p-4">
          <p className="text-sm text-rose-700">{error}</p>
        </Card>
      )}

      {steps.length > 0 && (
        <Card className="p-5">
          <h3 className="mb-3 font-semibold text-ink">
            {zh ? "执行进度" : "Progress"}
          </h3>
          <ProgressTimeline locale={locale} steps={steps} />
        </Card>
      )}

      {summary && (
        <Card className="p-5">
          <h3 className="mb-3 font-semibold text-ink">
            {zh ? "发现结果" : "Discovery Results"}
          </h3>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            {[
              [summary.total_candidates, zh ? "候选链接" : "Candidates"],
              [summary.pages_fetched, zh ? "已抓页面" : "Pages fetched"],
              [summary.programs_extracted, zh ? "抽取项目" : "Programs extracted"],
              [summary.pages_skipped, zh ? "跳过" : "Skipped"],
            ].map(([v, label]) => (
              <div key={String(label)} className="rounded-xl bg-gray-50 p-3 text-center">
                <div className="text-xl font-bold text-ink">{String(v)}</div>
                <div className="text-xs text-muted">{String(label)}</div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {programs.length > 0 && (
        <div>
          <h3 className="mb-3 font-semibold text-ink">
            {zh ? `发现 ${programs.length} 个项目` : `${programs.length} programs found`}
          </h3>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {programs.map((p: any) => (
              <ProgramResultCard key={p.id} program={p} locale={locale} />
            ))}
          </div>
        </div>
      )}

      {result && programs.length === 0 && !loading && (
        <Card className="p-8 text-center">
          <p className="text-muted">
            {zh ? "未发现项目。请尝试其他学校或方向。" : "No programs found. Try a different university or field."}
          </p>
        </Card>
      )}
    </div>
  );
}
