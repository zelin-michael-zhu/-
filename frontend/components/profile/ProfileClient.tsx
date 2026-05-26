"use client";

import { useEffect, useMemo, useState } from "react";
import { analyzeApplicant, getDefaultApplicant, updateApplicant } from "@/lib/api";
import type { Applicant, ProfileAnalysis } from "@/lib/types";
import { ActionResult } from "../common/ActionResult";
import { Button } from "../common/Button";
import { Card } from "../common/Card";
import { GpaConverterCard } from "./GpaConverterCard";

type FormState = {
  full_name: string;
  email: string;
  university: string;
  college: string;
  major: string;
  degree: string;
  graduation_year: string;
  gpa_value: string;
  gpa_scale: string;
  ranking: string;
  ielts: string;
  toefl: string;
  gre: string;
  gmat: string;
  target_countries: string;
  target_fields: string;
  preference_priority: string;
  budget: string;
  experiences: string;
  awards: string;
  papers: string;
};

function parseList(raw?: string | null) {
  if (!raw) return "";
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.join(", ") : "";
  } catch {
    return "";
  }
}

function toLines(raw?: string | null) {
  if (!raw) return "";
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.join("\n") : "";
  } catch {
    return "";
  }
}

function splitList(raw: string) {
  return raw.split(/,|\n/).map((item) => item.trim()).filter(Boolean);
}

function toNumber(raw: string) {
  if (!raw.trim()) return null;
  const value = Number(raw);
  return Number.isFinite(value) ? value : null;
}

function applicantToForm(applicant: Applicant): FormState {
  return {
    full_name: applicant.full_name || "",
    email: applicant.email || "",
    university: applicant.university || "",
    college: applicant.college || "",
    major: applicant.major || "",
    degree: applicant.degree || "",
    graduation_year: applicant.graduation_year ? String(applicant.graduation_year) : "",
    gpa_value: applicant.gpa_value ? String(applicant.gpa_value) : "",
    gpa_scale: applicant.gpa_scale ? String(applicant.gpa_scale) : "4",
    ranking: applicant.ranking || "",
    ielts: applicant.ielts ? String(applicant.ielts) : "",
    toefl: applicant.toefl ? String(applicant.toefl) : "",
    gre: applicant.gre ? String(applicant.gre) : "",
    gmat: applicant.gmat ? String(applicant.gmat) : "",
    target_countries: parseList(applicant.target_countries_json),
    target_fields: parseList(applicant.target_fields_json),
    preference_priority: applicant.preference_priority || "balanced",
    budget: applicant.budget ? String(applicant.budget) : "",
    experiences: toLines(applicant.experiences_json),
    awards: toLines(applicant.awards_json),
    papers: toLines(applicant.papers_json),
  };
}

export function ProfileClient({ locale }: { locale: string }) {
  const zh = locale === "zh";
  const [applicant, setApplicant] = useState<Applicant | null>(null);
  const [form, setForm] = useState<FormState | null>(null);
  const [analysis, setAnalysis] = useState<ProfileAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        setLoading(true);
        const current = await getDefaultApplicant();
        const currentAnalysis = await analyzeApplicant(current.id);
        if (!mounted) return;
        setApplicant(current);
        setForm(applicantToForm(current));
        setAnalysis(currentAnalysis);
      } catch (err) {
        if (mounted) setError(err instanceof Error ? err.message : String(err));
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  const fields = useMemo(() => [
    ["full_name", zh ? "姓名" : "Full name"],
    ["email", zh ? "邮箱" : "Email"],
    ["university", zh ? "本科院校" : "University"],
    ["college", zh ? "学院" : "College"],
    ["major", zh ? "专业" : "Major"],
    ["degree", zh ? "学位" : "Degree"],
    ["graduation_year", zh ? "毕业年份" : "Graduation year"],
    ["ranking", zh ? "排名" : "Ranking"],
    ["ielts", "IELTS"],
    ["toefl", "TOEFL"],
    ["gre", "GRE"],
    ["gmat", "GMAT"],
    ["budget", zh ? "预算" : "Budget"],
  ] as const, [zh]);

  function updateField(key: keyof FormState, value: string) {
    setForm((current) => current ? { ...current, [key]: value } : current);
  }

  async function save() {
    if (!applicant || !form) return;
    setSaving(true);
    setSuccess(null);
    setError(null);
    try {
      const saved = await updateApplicant(applicant.id, {
        full_name: form.full_name,
        email: form.email,
        university: form.university,
        college: form.college,
        major: form.major,
        degree: form.degree,
        graduation_year: toNumber(form.graduation_year),
        gpa_value: toNumber(form.gpa_value),
        gpa_scale: toNumber(form.gpa_scale),
        ranking: form.ranking,
        ielts: toNumber(form.ielts),
        toefl: toNumber(form.toefl),
        gre: toNumber(form.gre),
        gmat: toNumber(form.gmat),
        target_countries_json: JSON.stringify(splitList(form.target_countries)),
        target_fields_json: JSON.stringify(splitList(form.target_fields)),
        preference_priority: form.preference_priority,
        budget: toNumber(form.budget),
        experiences_json: JSON.stringify(splitList(form.experiences)),
        awards_json: JSON.stringify(splitList(form.awards)),
        papers_json: JSON.stringify(splitList(form.papers)),
      });
      const freshAnalysis = await analyzeApplicant(saved.id);
      setApplicant(saved);
      setForm(applicantToForm(saved));
      setAnalysis(freshAnalysis);
      setSuccess(zh ? "已保存到 MySQL，刷新页面也不会丢。" : "Saved to MySQL. Refreshing will keep the data.");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSaving(false);
    }
  }

  async function analyze() {
    if (!applicant) return;
    setAnalyzing(true);
    setError(null);
    try {
      setAnalysis(await analyzeApplicant(applicant.id));
      setSuccess(zh ? "背景分析已更新。" : "Profile analysis updated.");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setAnalyzing(false);
    }
  }

  if (loading) return <Card className="p-6 text-sm text-muted">{zh ? "正在加载个人资料..." : "Loading profile..."}</Card>;
  if (!form || !applicant) return <ActionResult locale={locale} data={null} error={error || (zh ? "无法加载资料" : "Unable to load profile")} />;

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
      <Card className="p-6">
        <div className="mb-6 flex flex-wrap gap-2">
          {(zh ? ["教育背景", "GPA", "语言/标化", "经历", "偏好"] : ["Education", "GPA", "Test Scores", "Experiences", "Preferences"]).map((step, index) => (
            <span key={step} className={`rounded-full px-3 py-1 text-sm ${index === 0 ? "bg-ink text-white" : "bg-gray-100 text-muted"}`}>{step}</span>
          ))}
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {fields.map(([key, label]) => (
            <label key={key} className="text-sm font-medium">
              {label}
              <input value={form[key]} onChange={(event) => updateField(key, event.target.value)} className="mt-2 w-full rounded-xl border border-line px-3 py-2 outline-none focus:border-brand" />
            </label>
          ))}
          <label className="text-sm font-medium">
            GPA
            <div className="mt-2 grid grid-cols-[1fr_110px] gap-2">
              <input value={form.gpa_value} onChange={(event) => updateField("gpa_value", event.target.value)} className="rounded-xl border border-line px-3 py-2 outline-none focus:border-brand" />
              <select value={form.gpa_scale} onChange={(event) => updateField("gpa_scale", event.target.value)} className="rounded-xl border border-line px-3 py-2 outline-none focus:border-brand">
                <option value="4">4.0</option>
                <option value="5">5.0</option>
                <option value="100">100</option>
              </select>
            </div>
          </label>
          <label className="text-sm font-medium">
            {zh ? "申请偏好" : "Preference priority"}
            <select value={form.preference_priority} onChange={(event) => updateField("preference_priority", event.target.value)} className="mt-2 w-full rounded-xl border border-line px-3 py-2 outline-none focus:border-brand">
              <option value="balanced">{zh ? "均衡" : "Balanced"}</option>
              <option value="ranking">{zh ? "排名优先" : "Ranking first"}</option>
              <option value="cost">{zh ? "预算优先" : "Cost first"}</option>
              <option value="career">{zh ? "就业优先" : "Career first"}</option>
            </select>
          </label>
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <label className="text-sm font-medium">{zh ? "目标国家/地区，逗号分隔" : "Target countries, comma-separated"}<textarea value={form.target_countries} onChange={(event) => updateField("target_countries", event.target.value)} className="mt-2 h-24 w-full rounded-xl border border-line px-3 py-2 outline-none focus:border-brand" /></label>
          <label className="text-sm font-medium">{zh ? "目标方向，逗号分隔" : "Target fields, comma-separated"}<textarea value={form.target_fields} onChange={(event) => updateField("target_fields", event.target.value)} className="mt-2 h-24 w-full rounded-xl border border-line px-3 py-2 outline-none focus:border-brand" /></label>
          <label className="text-sm font-medium">{zh ? "经历，一行一个" : "Experiences, one per line"}<textarea value={form.experiences} onChange={(event) => updateField("experiences", event.target.value)} className="mt-2 h-28 w-full rounded-xl border border-line px-3 py-2 outline-none focus:border-brand" /></label>
          <label className="text-sm font-medium">{zh ? "奖项，一行一个" : "Awards, one per line"}<textarea value={form.awards} onChange={(event) => updateField("awards", event.target.value)} className="mt-2 h-28 w-full rounded-xl border border-line px-3 py-2 outline-none focus:border-brand" /></label>
          <label className="text-sm font-medium md:col-span-2">{zh ? "论文/研究，一行一个" : "Papers / research, one per line"}<textarea value={form.papers} onChange={(event) => updateField("papers", event.target.value)} className="mt-2 h-24 w-full rounded-xl border border-line px-3 py-2 outline-none focus:border-brand" /></label>
        </div>
        <div className="mt-6 flex flex-wrap items-center gap-3">
          <Button onClick={save} disabled={saving}>{saving ? (zh ? "保存中..." : "Saving...") : (zh ? "保存资料" : "Save Profile")}</Button>
          <Button onClick={analyze} disabled={analyzing}>{analyzing ? (zh ? "分析中..." : "Analyzing...") : (zh ? "分析背景" : "Analyze Profile")}</Button>
          {success && <span className="text-sm font-medium text-emerald-700">{success}</span>}
          {error && <span className="text-sm font-medium text-rose-700">{error}</span>}
        </div>
      </Card>
      <div className="space-y-6">
        <GpaConverterCard locale={locale} value={applicant.gpa_value} scale={applicant.gpa_scale} converted={applicant.gpa_converted_4} />
        <Card className="p-5">
          <h3 className="font-semibold">{zh ? "背景分析" : "Profile Analysis"}</h3>
          {analysis ? (
            <div className="mt-4 space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-xl bg-indigo-50 p-3 text-indigo-700"><b>{analysis.profile_strength_score}%</b><br />{zh ? "竞争力" : "Strength"}</div>
                <div className="rounded-xl bg-emerald-50 p-3 text-emerald-700"><b>{analysis.completeness_percentage}%</b><br />{zh ? "完整度" : "Completeness"}</div>
              </div>
              <Section title={zh ? "优势" : "Strengths"} items={analysis.strengths} />
              <Section title={zh ? "风险" : "Weaknesses"} items={analysis.weaknesses} />
              <Section title={zh ? "建议" : "Suggested Improvements"} items={analysis.suggested_improvements} />
            </div>
          ) : <p className="mt-3 text-sm text-muted">{zh ? "点击分析背景生成结果。" : "Click Analyze Profile to generate insights."}</p>}
        </Card>
      </div>
    </div>
  );
}

function Section({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null;
  return <div><div className="font-semibold text-ink">{title}</div><ul className="mt-2 space-y-1 text-muted">{items.map((item) => <li key={item}>- {item}</li>)}</ul></div>;
}
