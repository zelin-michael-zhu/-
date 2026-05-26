"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ProgramCard } from "@/components/programs/ProgramCard";
import { ProgramFilters, type ProgramFilterState } from "@/components/programs/ProgramFilters";
import { getPrograms } from "@/lib/api";
import type { Program } from "@/lib/types";

const initialFilters: ProgramFilterState = { search: "", country: "", field: "", university: "", review_status: "", min_confidence: "" };

export default function Programs({ params }: { params: Promise<{ locale: string }> }) {
  const [locale, setLocale] = useState("en");
  const [programs, setPrograms] = useState<Program[]>([]);
  const [filters, setFilters] = useState(initialFilters);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    params.then(({ locale }) => setLocale(locale));
  }, [params]);

  useEffect(() => {
    let mounted = true;
    const timer = setTimeout(async () => {
      try {
        setLoading(true);
        setError(null);
        const items = await getPrograms(filters);
        if (mounted) setPrograms(items);
      } catch (err) {
        if (mounted) setError(err instanceof Error ? err.message : String(err));
      } finally {
        if (mounted) setLoading(false);
      }
    }, 250);
    return () => {
      mounted = false;
      clearTimeout(timer);
    };
  }, [filters]);

  return <AppShell locale={locale}><div className="mb-6"><h1 className="text-3xl font-bold">{locale === "zh" ? "项目数据库" : "Program Database"}</h1><p className="mt-2 text-muted">{locale === "zh" ? "所有自动抽取数据都需要以官网核对。" : "All auto-extracted data must be verified with official websites."}</p></div><ProgramFilters locale={locale} filters={filters} onChange={setFilters} />{loading && <div className="mt-6 rounded-2xl border border-line bg-white p-5 text-sm text-muted">{locale === "zh" ? "正在加载项目..." : "Loading programs..."}</div>}{error && <div className="mt-6 rounded-2xl border border-rose-200 bg-rose-50 p-5 text-sm text-rose-700">{error}</div>}<div className="mt-6 grid gap-5">{!loading && programs.length === 0 && <div className="rounded-2xl border border-line bg-white p-5 text-sm text-muted">{locale === "zh" ? "没有符合筛选的项目。" : "No programs match the filters."}</div>}{programs.map((p) => <ProgramCard key={p.id} program={p} locale={locale} />)}</div></AppShell>;
}
