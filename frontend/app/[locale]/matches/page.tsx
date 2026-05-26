"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { addApplication, generateMatches, generateRecommendations, getDefaultApplicant, getMatches } from "@/lib/api";
import { tValue } from "@/lib/display";
import type { Applicant, ProgramMatch } from "@/lib/types";

const columns = ["Strong Target", "Target", "Safety", "Reach", "Not Recommended"];

export default function Matches({ params }: { params: Promise<{ locale: string }> }) {
  const [locale, setLocale] = useState("en");
  const zh = locale === "zh";
  const [applicant, setApplicant] = useState<Applicant | null>(null);
  const [matches, setMatches] = useState<ProgramMatch[]>([]);
  const [applications, setApplications] = useState<Record<number, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<any>(null);

  useEffect(() => {
    params.then(({ locale }) => setLocale(locale));
  }, [params]);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const current = await getDefaultApplicant();
      setApplicant(current);
      setMatches(await getMatches(current.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function generate() {
    if (!applicant) return;
    setGenerating(true);
    setError(null);
    setMessage(null);
    try {
      const result = await generateMatches(applicant.id);
      setMatches(result.items);
      setMessage(zh ? `已生成 ${result.total} 个匹配。` : `Generated ${result.total} matches.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setGenerating(false);
    }
  }

  async function add(match: ProgramMatch) {
    if (!applicant) return;
    setError(null);
    try {
      await addApplication(applicant.id, match.program.id);
      setApplications((current) => ({ ...current, [match.program.id]: true }));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  async function generateAiRecommendations() {
    if (!applicant) return;
    setGenerating(true);
    setError(null);
    try {
      setRecommendations(await generateRecommendations(applicant.id, "mock"));
      setMessage(zh ? "AI 推荐已生成，请核对官网证据。" : "AI recommendations generated. Verify official evidence.");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setGenerating(false);
    }
  }

  return (
    <AppShell locale={locale}>
      <h1 className="mb-6 text-3xl font-bold">{zh ? "项目匹配" : "Matches"}</h1>
      <Card className="mb-6 p-5">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h3 className="font-semibold">{zh ? "匹配引擎" : "Matching Engine"}</h3>
            <p className="mt-2 text-sm text-muted">{zh ? "基于你保存到 MySQL 的背景资料和真实项目库重新计算匹配。" : "Generate match scores from your saved MySQL profile and the real program database."}</p>
            {message && <p className="mt-2 text-sm font-medium text-emerald-700">{message}</p>}
            {error && <p className="mt-2 text-sm font-medium text-rose-700">{error}</p>}
          </div>
          <div className="flex flex-wrap gap-3">
            <Button disabled={loading || generating} onClick={generate}>{generating ? (zh ? "生成中..." : "Generating...") : (zh ? "生成匹配" : "Generate Matches")}</Button>
            <Button disabled={loading || generating} onClick={generateAiRecommendations}>{zh ? "生成 AI 推荐" : "Generate AI Recommendations"}</Button>
          </div>
        </div>
      </Card>
      {recommendations?.recommendations?.length ? (
        <Card className="mb-6 p-5">
          <h3 className="font-semibold">{zh ? "AI 推荐组合" : "AI Recommendation Portfolio"}</h3>
          <p className="mt-2 text-sm text-amber-700">{zh ? "AI 推荐基于官网证据字段生成，申请前仍必须核对学校官网。" : "AI recommendations use source evidence fields. Verify with the official website before applying."}</p>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {recommendations.recommendations.slice(0, 4).map((item: any) => (
              <div key={item.program_id} className="rounded-xl bg-gray-50 p-4">
                <div className="flex items-start justify-between gap-3"><div className="font-semibold">{item.program_name}</div><Badge tone="brand">{Math.round(item.score)}</Badge></div>
                <p className="mt-2 text-xs text-muted">{item.ai_reason}</p>
                <p className="mt-2 text-xs text-amber-700">{item.missing_requirements?.join(", ") || (zh ? "暂无缺失材料" : "No missing requirements")}</p>
                <p className="mt-2 break-all text-xs text-muted">{item.evidence?.[0]?.source_url}</p>
              </div>
            ))}
          </div>
        </Card>
      ) : null}
      {loading ? <Card className="p-5 text-sm text-muted">{zh ? "正在加载匹配..." : "Loading matches..."}</Card> : (
        <>
          {!matches.length && <Card className="mb-6 p-5 text-sm text-muted">{zh ? "还没有匹配结果，点击上方按钮生成。" : "No matches yet. Click Generate Matches to start."}</Card>}
          <div className="grid gap-4 xl:grid-cols-5">
            {columns.map((column) => (
              <Card key={column} className="p-4">
                <h3 className="font-semibold">{tValue(column, locale)}</h3>
                <div className="mt-4 space-y-3">
                  {matches.filter((match) => match.category === column).map((match) => (
                    <div key={match.id} className="rounded-xl bg-gray-50 p-3">
                      <div className="text-sm font-semibold">{match.program.program_name}</div>
                      <div className="mt-1 text-xs text-muted">{match.program.university_name} · {tValue(match.program.country, locale)} · {tValue(match.program.field, locale)}</div>
                      <div className="mt-2 flex justify-between"><span className="text-xs text-muted">{tValue(match.category, locale)}</span><Badge tone="brand">{Math.round(match.match_score)}</Badge></div>
                      <p className="mt-2 text-xs text-muted">{match.reasons[0] || (zh ? "方向和地区匹配。" : "Profile and program fit.")}</p>
                      {match.risks.length > 0 && <p className="mt-1 text-xs text-amber-700">{match.risks[0]}</p>}
                      <button onClick={() => add(match)} disabled={applications[match.program.id]} className="mt-3 w-full rounded-xl bg-ink px-3 py-2 text-xs font-semibold text-white disabled:bg-emerald-600">
                        {applications[match.program.id] ? (zh ? "已加入申请" : "Added") : (zh ? "加入申请列表" : "Add to Application List")}
                      </button>
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </>
      )}
    </AppShell>
  );
}
