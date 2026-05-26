"use client";

import { useEffect, useState } from "react";
import { getDashboard, getDefaultApplicant } from "@/lib/api";
import type { DashboardData } from "@/lib/types";
import { tValue } from "@/lib/display";
import { Badge } from "../common/Badge";
import { Card } from "../common/Card";
import { StatCard } from "./StatCard";

export function DashboardClient({ locale }: { locale: string }) {
  const zh = locale === "zh";
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        setLoading(true);
        const applicant = await getDefaultApplicant();
        const dashboard = await getDashboard(applicant.id);
        if (mounted) setData(dashboard);
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

  if (loading) return <Card className="p-6 text-sm text-muted">{zh ? "正在加载申请总览..." : "Loading dashboard..."}</Card>;
  if (error) return <Card className="p-6 text-sm text-rose-700">{error}</Card>;
  if (!data) return null;

  const stats = data.stats;
  const statuses = ["Not Started", "In Progress", "Submitted", "Interview", "Offer", "Rejected"];

  return (
    <>
      <div className="mb-6">
        <p className="text-sm text-muted">{zh ? `欢迎回来，${data.applicant.full_name}` : `Welcome back, ${data.applicant.full_name}`}</p>
        <h1 className="text-3xl font-bold">{zh ? "申请总览" : "Application Dashboard"}</h1>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label={zh ? "背景竞争力" : "Profile Strength"} value={`${stats.profile_strength}%`} hint={`${data.profile_analysis.completeness_percentage}% ${zh ? "资料完整度" : "complete"}`} />
        <StatCard label={zh ? "项目总数" : "Total Programs"} value={String(stats.total_programs)} hint={zh ? "来自 MySQL 项目库" : "From MySQL program database"} />
        <StatCard label={zh ? "匹配项目" : "Matched Programs"} value={String(stats.matched_programs)} hint={zh ? "由真实背景生成" : "Generated from real profile"} />
        <StatCard label={zh ? "申请中" : "Applications"} value={String(stats.applications)} hint={`${stats.upcoming_deadlines} ${zh ? "个近期截止" : "upcoming deadlines"}`} />
      </div>
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card className="p-5">
          <h3 className="font-semibold">{zh ? "Top 项目匹配" : "Top Program Matches"}</h3>
          <div className="mt-4 space-y-3">
            {data.top_matches.length ? data.top_matches.map((match) => (
              <div key={match.id} className="rounded-xl bg-gray-50 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-semibold">{match.program.program_name}</div>
                    <div className="mt-1 text-xs text-muted">{match.program.university_name} · {tValue(match.program.country, locale)}</div>
                  </div>
                  <Badge tone="brand">{Math.round(match.match_score)}</Badge>
                </div>
              </div>
            )) : <p className="text-sm text-muted">{zh ? "还没有匹配结果，请去项目匹配页生成。" : "No matches yet. Generate them on the Matches page."}</p>}
          </div>
        </Card>
        <Card className="p-5">
          <h3 className="font-semibold">{zh ? "近期截止日期" : "Upcoming Deadlines"}</h3>
          <div className="mt-4 space-y-3">
            {data.upcoming_deadlines.length ? data.upcoming_deadlines.map((item) => (
              <div key={item.id} className="flex items-center justify-between rounded-xl bg-gray-50 p-3 text-sm">
                <span className="font-medium">{item.program?.program_name}</span>
                <span className="text-muted">{item.deadline || "TBC"}</span>
              </div>
            )) : <p className="text-sm text-muted">{zh ? "暂无申请截止日期。" : "No application deadlines yet."}</p>}
          </div>
        </Card>
        <Card className="p-5">
          <h3 className="font-semibold">{zh ? "我的任务" : "My Tasks"}</h3>
          <div className="mt-4 space-y-2">
            {data.tasks.length ? data.tasks.map((task) => (
              <div key={task.title} className="rounded-xl border border-line p-3 text-sm">
                <div className="font-medium">{task.title}</div>
                <div className="mt-1 text-xs text-muted">{task.type} · {task.priority}</div>
              </div>
            )) : <p className="text-sm text-muted">{zh ? "目前没有阻塞任务。" : "No blocking tasks right now."}</p>}
          </div>
        </Card>
        <Card className="p-5">
          <h3 className="font-semibold">{zh ? "申请进度预览" : "Application Pipeline"}</h3>
          <div className="mt-5 grid grid-cols-3 gap-2 text-center text-xs text-muted md:grid-cols-6">
            {statuses.map((status) => (
              <div key={status} className="rounded-xl bg-gray-50 p-3">
                {tValue(status, locale)}<br /><b>{data.applications_by_status[status] || 0}</b>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </>
  );
}
