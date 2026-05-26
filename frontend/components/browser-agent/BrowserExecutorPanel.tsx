"use client";

import { useEffect, useState } from "react";
import { MonitorCog, ShieldCheck } from "lucide-react";
import { approveBrowserAction, getBrowserExecutors, getBrowserLogs, getDefaultApplicant, getOpenCliStatus, getPrograms, runBrowserTaskNextStep, startBrowserTask, stopBrowserTask } from "@/lib/api";
import type { Applicant, Program } from "@/lib/types";
import { ActionResult } from "../common/ActionResult";
import { Badge } from "../common/Badge";
import { Button } from "../common/Button";
import { Card } from "../common/Card";

export function BrowserExecutorPanel({ locale }: { locale: string }) {
  const zh = locale === "zh";
  const [executorType, setExecutorType] = useState("mock");
  const [taskId, setTaskId] = useState<number | null>(null);
  const [applicant, setApplicant] = useState<Applicant | null>(null);
  const [programs, setPrograms] = useState<Program[]>([]);
  const [programId, setProgramId] = useState<number | null>(null);
  const [executors, setExecutors] = useState<unknown>(null);
  const [opencli, setOpencli] = useState<unknown>(null);
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<string | null>(null);

  const options = [
    {
      type: "mock",
      title: zh ? "Mock Demo" : "Mock Demo",
      description: zh ? "使用模拟浏览器动作进行界面测试。" : "Use simulated browser actions for UI testing.",
    },
    {
      type: "playwright",
      title: zh ? "Playwright 本地表单" : "Playwright Local Form",
      description: zh ? "使用 Playwright 填写本地示例申请表。" : "Use Playwright to fill a local sample application form.",
    },
    {
      type: "opencli",
      title: zh ? "OpenCLI 已登录 Chrome" : "OpenCLI Logged-in Chrome",
      description: zh ? "通过 OpenCLI 使用你本地已登录的 Chrome 会话。" : "Use your local logged-in Chrome session through OpenCLI.",
    },
  ];

  async function run(label: string, fn: () => Promise<unknown>) {
    setLoading(label);
    setError(null);
    setResult(null);
    try {
      const json = await fn();
      setResult(json);
      const maybeId = (json as { id?: number; task_id?: number }).id || (json as { id?: number; task_id?: number }).task_id;
      if (maybeId) setTaskId(maybeId);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(null);
    }
  }

  async function refreshStatus() {
    const [executorJson, opencliJson] = await Promise.all([getBrowserExecutors(), getOpenCliStatus()]);
    setExecutors(executorJson);
    setOpencli(opencliJson);
  }

  useEffect(() => {
    async function load() {
      const [currentApplicant, programItems] = await Promise.all([getDefaultApplicant(), getPrograms({ limit: 20 })]);
      setApplicant(currentApplicant);
      setPrograms(programItems);
      setProgramId(programItems[0]?.id || null);
      await refreshStatus();
    }
    load().catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  return (
    <Card className="p-5">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
        <div>
          <div className="flex items-center gap-2 font-semibold">
            <MonitorCog size={18} className="text-brand" />
            {zh ? "执行器选择" : "Executor Selector"}
          </div>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-muted">
            {zh
              ? "OpenCLI 是外部浏览器执行器，ApplyPilot 只通过后端受控调用它。未安装时项目仍正常运行。"
              : "OpenCLI is an external browser executor. ApplyPilot only calls it through the backend executor layer. The project still runs when OpenCLI is unavailable."}
          </p>
        </div>
        <Badge tone="warning">{zh ? "高风险动作需确认" : "High-risk actions gated"}</Badge>
      </div>

      <div className="mt-5 grid gap-3 lg:grid-cols-3">
        {options.map((option) => (
          <button
            key={option.type}
            onClick={() => setExecutorType(option.type)}
            className={`rounded-2xl border p-4 text-left transition ${executorType === option.type ? "border-brand bg-indigo-50" : "border-line bg-gray-50 hover:border-brand hover:bg-white"}`}
          >
            <div className="font-semibold">{option.title}</div>
            <p className="mt-2 text-xs leading-5 text-muted">{option.description}</p>
          </button>
        ))}
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-2">
        <div className="rounded-2xl border border-line bg-gray-50 p-4 text-sm">
          <div className="font-semibold">{zh ? "当前申请人" : "Current Applicant"}</div>
          <p className="mt-2 text-muted">{applicant ? `${applicant.full_name} · ${applicant.email}` : (zh ? "加载中" : "Loading")}</p>
          <p className="mt-1 text-muted">{applicant?.university} · {applicant?.major} · GPA {applicant?.gpa_converted_4 || applicant?.gpa_value || "--"}</p>
        </div>
        <label className="rounded-2xl border border-line bg-gray-50 p-4 text-sm font-semibold">
          {zh ? "目标项目" : "Target Program"}
          <select value={programId || ""} onChange={(event) => setProgramId(Number(event.target.value))} className="mt-2 w-full rounded-xl border border-line bg-white px-3 py-2 text-sm font-normal">
            {programs.map((program) => <option key={program.id} value={program.id}>{program.program_name}</option>)}
          </select>
        </label>
      </div>

      <div className="mt-5 grid gap-2 md:grid-cols-3 xl:grid-cols-6">
        <Button disabled={loading !== null} onClick={() => run("check", refreshStatus)}>{zh ? "检查 OpenCLI" : "Check OpenCLI"}</Button>
        <Button disabled={loading !== null || !applicant || !programId} onClick={() => run("start", () => startBrowserTask(applicant!.id, programId!, executorType))}>{zh ? "开始任务" : "Start Task"}</Button>
        <Button disabled={loading !== null || taskId === null} onClick={() => run("next", () => runBrowserTaskNextStep(taskId!))}>{zh ? "下一步" : "Run Next Step"}</Button>
        <Button disabled={loading !== null || taskId === null} onClick={() => run("approve", () => approveBrowserAction(taskId!, "next"))}>{zh ? "批准" : "Approve"}</Button>
        <button disabled={loading !== null || taskId === null} onClick={() => run("stop", () => stopBrowserTask(taskId!))} className="rounded-xl bg-rose-600 px-4 py-2.5 text-sm font-semibold text-white disabled:bg-gray-300">{zh ? "停止任务" : "Stop Task"}</button>
        <button disabled={loading !== null || taskId === null} onClick={() => run("logs", () => getBrowserLogs(taskId!))} className="rounded-xl border border-line bg-white px-4 py-2.5 text-sm font-semibold disabled:text-gray-400">{zh ? "查看日志" : "View Logs"}</button>
      </div>

      <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
        <div className="flex items-center gap-2 font-semibold"><ShieldCheck size={16} />{zh ? "安全提示" : "Safety Notice"}</div>
        <p className="mt-2">{zh ? "最终提交和付款已禁用。ApplyPilot 会在高风险操作前停止。" : "Final submission and payment are disabled. ApplyPilot always stops before high-risk actions."}</p>
      </div>

      {Boolean(opencli) && !(opencli as { installed?: boolean }).installed && (
        <div className="mt-5 rounded-2xl border border-line bg-white p-4 text-sm text-muted">
          {zh ? "未检测到 OpenCLI。请先安装：" : "OpenCLI is not installed. Install it with:"}
          <pre className="mt-2 rounded-xl bg-gray-950 p-3 text-xs text-gray-100">npm install -g @jackwener/opencli{"\n"}opencli doctor</pre>
        </div>
      )}

      <ActionResult locale={locale} title={zh ? "执行器状态" : "Executor Status"} data={executors} />
      <ActionResult locale={locale} title={zh ? "OpenCLI 状态" : "OpenCLI Status"} data={opencli} />
      <ActionResult locale={locale} title={zh ? "操作反馈" : "Action Result"} data={result} error={error} />
    </Card>
  );
}
