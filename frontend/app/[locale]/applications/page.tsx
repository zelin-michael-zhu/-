"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/common/Card";
import { getApplications, getDefaultApplicant, updateApplicationStatus } from "@/lib/api";
import { tValue } from "@/lib/display";
import type { ApplicationItem } from "@/lib/types";

const statuses = ["Not Started", "In Progress", "Submitted", "Interview", "Offer", "Rejected"];

export default function Applications({ params }: { params: Promise<{ locale: string }> }) {
  const [locale, setLocale] = useState("en");
  const zh = locale === "zh";
  const [items, setItems] = useState<ApplicationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    params.then(({ locale }) => setLocale(locale));
  }, [params]);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const applicant = await getDefaultApplicant();
      setItems(await getApplications(applicant.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function move(applicationId: number, status: string) {
    setUpdating(applicationId);
    setError(null);
    try {
      const updated = await updateApplicationStatus(applicationId, status);
      setItems((current) => current.map((item) => item.id === applicationId ? updated : item));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setUpdating(null);
    }
  }

  return (
    <AppShell locale={locale} copilot={false}>
      <h1 className="mb-6 text-3xl font-bold">{zh ? "申请进度" : "Applications"}</h1>
      {loading && <Card className="p-5 text-sm text-muted">{zh ? "正在加载申请..." : "Loading applications..."}</Card>}
      {error && <Card className="mb-4 p-5 text-sm text-rose-700">{error}</Card>}
      {!loading && !items.length && <Card className="p-5 text-sm text-muted">{zh ? "还没有申请卡片，请从项目数据库或匹配页添加项目。" : "No applications yet. Add programs from the database or matches page."}</Card>}
      <div className="grid gap-4 xl:grid-cols-6">
        {statuses.map((status) => (
          <div key={status} className="rounded-2xl border border-line bg-white/70 p-3">
            <h3 className="mb-3 text-sm font-semibold">{tValue(status, locale)}</h3>
            <div className="space-y-3">
              {items.filter((item) => item.status === status).map((item) => (
                <Card key={item.id} className="p-4 shadow-none">
                  <div className="font-semibold">{item.program?.program_name || `Program #${item.program_id}`}</div>
                  <p className="mt-2 text-xs text-muted">{item.program?.university_name}</p>
                  <p className="mt-2 text-xs text-muted">{zh ? "截止日期" : "Deadline"} {item.deadline || "TBC"}</p>
                  {item.missing_items?.length ? <p className="mt-2 text-xs text-amber-700">{zh ? "缺失：" : "Missing: "}{item.missing_items.slice(0, 2).join(", ")}</p> : null}
                  <select value={item.status} disabled={updating === item.id} onChange={(event) => move(item.id, event.target.value)} className="mt-3 w-full rounded-xl border border-line px-2 py-2 text-xs">
                    {statuses.map((next) => <option key={next} value={next}>{tValue(next, locale)}</option>)}
                  </select>
                </Card>
              ))}
            </div>
          </div>
        ))}
      </div>
    </AppShell>
  );
}
