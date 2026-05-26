"use client";

import { useState } from "react";
import { ShieldCheck } from "lucide-react";
import { Button } from "../common/Button";
import { Card } from "../common/Card";
import { ActionResult } from "../common/ActionResult";

export function HumanApprovalCard({ locale }: { locale: string }) {
  const zh = locale === "zh";
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<number | null>(null);
  async function post(label: string, path: string) {
    setLoading(label);
    setError(null);
    setResult(null);
    try {
      const body = path === "/start-task"
        ? { applicant_id: 1, program_id: 1, executor_type: "mock" }
        : path === "/approve-action"
          ? { task_id: taskId, action_id: "next" }
          : { task_id: taskId };
      if (path !== "/start-task" && taskId === null) {
        throw new Error(zh ? "请先开始任务。" : "Start a task first.");
      }
      const response = await fetch(`http://127.0.0.1:8000/api/browser-agent${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      const json = await response.json();
      if (!response.ok) throw new Error(JSON.stringify(json));
      setResult(json);
      const nextTaskId = (json as { id?: number; task_id?: number }).id || (json as { id?: number; task_id?: number }).task_id;
      if (nextTaskId) setTaskId(nextTaskId);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(null);
    }
  }
  return <Card className="p-5"><div className="flex items-center gap-2 font-semibold"><ShieldCheck size={18} className="text-success" />{zh ? "人工确认" : "Human Approval"}</div><p className="mt-3 text-sm text-muted">{zh ? "AI 想填写这些字段：姓名、邮箱、学校、专业、GPA。" : "AI wants to fill these fields: name, email, university, major, GPA."}</p><div className="mt-4 grid grid-cols-2 gap-2"><Button disabled={loading !== null} onClick={() => post("start", "/start-task")}>{zh ? "开始任务" : "Start"}</Button><Button disabled={loading !== null} onClick={() => post("approve", "/approve-action")}>{zh ? "批准" : "Approve"}</Button><button className="rounded-xl border border-line bg-white px-4 py-2.5 text-sm font-semibold">{zh ? "编辑" : "Edit"}</button><button className="rounded-xl border border-line bg-white px-4 py-2.5 text-sm font-semibold">{zh ? "跳过" : "Skip"}</button><button onClick={() => post("stop", "/stop-task")} className="col-span-2 rounded-xl bg-rose-600 px-4 py-2.5 text-sm font-semibold text-white">{zh ? "停止任务" : "Stop Task"}</button></div><ActionResult locale={locale} data={result} error={error} /></Card>;
}
