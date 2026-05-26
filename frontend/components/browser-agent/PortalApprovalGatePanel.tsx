"use client";

import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, ExternalLink, LockKeyhole, Play, ShieldAlert, ShieldCheck, UserCheck } from "lucide-react";
import {
  approvePendingAction,
  confirmPortalLoggedIn,
  executePendingAction,
  generatePortalFillPlan,
  getDefaultApplicant,
  getPendingActions,
  getPortalLogs,
  getPrograms,
  markPendingActionUserCompleted,
  rejectPendingAction,
  runPortalFillStep,
  startPortalSession,
  stopPortalSession,
} from "@/lib/api";
import type { Applicant, PendingAction, PortalSession, Program } from "@/lib/types";
import { ActionResult } from "../common/ActionResult";
import { Badge } from "../common/Badge";
import { Button } from "../common/Button";
import { Card } from "../common/Card";

function riskTone(risk: string): "neutral" | "success" | "warning" | "danger" | "brand" {
  if (risk === "low") return "success";
  if (risk === "medium") return "warning";
  if (risk === "high") return "danger";
  return "neutral";
}

function valuePreview(value?: string | null) {
  if (!value) return "--";
  return value.length > 72 ? `${value.slice(0, 72)}...` : value;
}

export function PortalApprovalGatePanel({ locale }: { locale: string }) {
  const zh = locale === "zh";
  const [applicant, setApplicant] = useState<Applicant | null>(null);
  const [programs, setPrograms] = useState<Program[]>([]);
  const [programId, setProgramId] = useState<number | null>(null);
  const [executorType, setExecutorType] = useState("mock");
  const [portalUrl, setPortalUrl] = useState("https://example.edu/apply");
  const [snapshotText, setSnapshotText] = useState("");
  const [session, setSession] = useState<PortalSession | null>(null);
  const [actions, setActions] = useState<PendingAction[]>([]);
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<unknown>(null);

  const grouped = useMemo(() => ({
    low: actions.filter((item) => item.risk_level === "low"),
    medium: actions.filter((item) => item.risk_level === "medium"),
    blocked: actions.filter((item) => item.blocked || item.risk_level === "high"),
  }), [actions]);

  async function run(label: string, fn: () => Promise<unknown>, refresh = true) {
    setLoading(label);
    setError(null);
    try {
      const json = await fn();
      setResult(json);
      const maybeSession = json as Partial<PortalSession>;
      const nestedSession = (json as { session?: PortalSession }).session;
      if (nestedSession?.id) setSession(nestedSession);
      else if (maybeSession.id && maybeSession.status) setSession(maybeSession as PortalSession);
      if (session?.id && refresh) await refreshActions(session.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(null);
    }
  }

  async function refreshActions(sessionId: number) {
    const json = await getPendingActions(sessionId);
    setActions(json.items);
  }

  async function start() {
    if (!applicant) return;
    await run("start", async () => {
      const started = await startPortalSession(applicant.id, programId, executorType, portalUrl, snapshotText || undefined);
      setSession(started);
      const pending = await getPendingActions(started.id);
      setActions(pending.items);
      return started;
    }, false);
  }

  async function loggedIn() {
    if (!session) return;
    await run("login", () => confirmPortalLoggedIn(session.id, snapshotText || undefined));
  }

  async function generatePlan() {
    if (!session) return;
    await run("plan", async () => {
      const json = await generatePortalFillPlan(session.id, snapshotText || undefined);
      setSession(json.session);
      setActions(json.items);
      return json;
    }, false);
  }

  async function approveAndRun(action: PendingAction) {
    await run("approve-run", async () => {
      await approvePendingAction(action.id);
      const executed = await executePendingAction(action.id);
      if (session) await refreshActions(session.id);
      return executed;
    }, false);
  }

  async function autoRun(action: PendingAction) {
    await run("auto-run", async () => {
      const executed = await executePendingAction(action.id);
      if (session) await refreshActions(session.id);
      return executed;
    }, false);
  }

  async function reject(action: PendingAction) {
    await run("reject", async () => {
      const rejected = await rejectPendingAction(action.id);
      if (session) await refreshActions(session.id);
      return rejected;
    }, false);
  }

  async function manual(action: PendingAction) {
    await run("manual", async () => {
      const completed = await markPendingActionUserCompleted(action.id);
      if (session) await refreshActions(session.id);
      return completed;
    }, false);
  }

  useEffect(() => {
    async function load() {
      const [currentApplicant, programItems] = await Promise.all([getDefaultApplicant(), getPrograms({ limit: 20 })]);
      setApplicant(currentApplicant);
      setPrograms(programItems);
      setProgramId(programItems[0]?.id || null);
    }
    load().catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  return (
    <Card className="p-5">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <div className="flex items-center gap-2 text-lg font-semibold">
            <ShieldCheck size={20} className="text-brand" />
            {zh ? "Portal Assistant 人工确认闸门" : "Portal Assistant Human Approval Gate"}
          </div>
          <p className="mt-2 max-w-4xl text-sm leading-6 text-muted">
            {zh
              ? "所有浏览器动作都会先进入 ApplyPilot 后端，由 RiskGuard 分类。低风险可自动执行，中风险必须确认，高风险只允许你本人在学校官网手动完成。"
              : "Every browser action enters the ApplyPilot backend first for RiskGuard classification. Low-risk actions can run automatically, medium-risk actions require approval, and high-risk actions must be completed manually on the official portal."}
          </p>
        </div>
        <Badge tone="danger">{zh ? "Final submit / payment 永不自动执行" : "Final submit / payment never automated"}</Badge>
      </div>

      <div className="mt-5 grid gap-3 lg:grid-cols-4">
        <label className="text-sm font-semibold">
          {zh ? "执行器" : "Executor"}
          <select value={executorType} onChange={(event) => setExecutorType(event.target.value)} className="mt-2 w-full rounded-xl border border-line bg-white px-3 py-2 text-sm font-normal">
            <option value="mock">Mock</option>
            <option value="playwright">Playwright</option>
            <option value="opencli">OpenCLI</option>
          </select>
        </label>
        <label className="text-sm font-semibold lg:col-span-2">
          {zh ? "Portal URL" : "Portal URL"}
          <input value={portalUrl} onChange={(event) => setPortalUrl(event.target.value)} className="mt-2 w-full rounded-xl border border-line bg-white px-3 py-2 text-sm font-normal" />
        </label>
        <label className="text-sm font-semibold">
          {zh ? "目标项目" : "Program"}
          <select value={programId || ""} onChange={(event) => setProgramId(Number(event.target.value))} className="mt-2 w-full rounded-xl border border-line bg-white px-3 py-2 text-sm font-normal">
            {programs.map((program) => <option key={program.id} value={program.id}>{program.program_name}</option>)}
          </select>
        </label>
      </div>

      <label className="mt-4 block text-sm font-semibold">
        {zh ? "页面快照 / 测试输入" : "Page Snapshot / Test Input"}
        <textarea
          value={snapshotText}
          onChange={(event) => setSnapshotText(event.target.value)}
          placeholder={zh ? "可输入 captcha / login / field labels 来模拟门户状态" : "Optional: type captcha / login / field labels to simulate portal state"}
          className="mt-2 min-h-20 w-full rounded-xl border border-line bg-white px-3 py-2 text-sm font-normal"
        />
      </label>

      <div className="mt-5 grid gap-2 md:grid-cols-3 xl:grid-cols-6">
        <Button disabled={loading !== null || !applicant} onClick={start}><Play size={15} />{zh ? "Start" : "Start"}</Button>
        <Button disabled={loading !== null || !session} onClick={loggedIn}><UserCheck size={15} />{zh ? "我已登录" : "I Logged In"}</Button>
        <Button disabled={loading !== null || !session} onClick={generatePlan}>{zh ? "生成动作计划" : "Generate Fill Plan"}</Button>
        <Button disabled={loading !== null || !session} onClick={() => session && run("step", () => runPortalFillStep(session.id))}>{zh ? "运行下一步" : "Run Next Step"}</Button>
        <button disabled={loading !== null || !session} onClick={() => session && run("logs", () => getPortalLogs(session.id), false)} className="rounded-xl border border-line bg-white px-4 py-2.5 text-sm font-semibold disabled:text-gray-400">{zh ? "查看日志" : "View Log"}</button>
        <button disabled={loading !== null || !session} onClick={() => session && run("stop", () => stopPortalSession(session.id))} className="rounded-xl bg-rose-600 px-4 py-2.5 text-sm font-semibold text-white disabled:bg-gray-300">{zh ? "停止" : "Stop"}</button>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-3">
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
          <div className="font-semibold">{zh ? "低风险，系统可自动执行" : "Low Risk: Auto-runnable"}</div>
          <p className="mt-2">{zh ? "这是低风险操作，ApplyPilot 可以自动完成，并会记录日志。" : "ApplyPilot can automate these low-risk actions and records an audit log."}</p>
          <div className="mt-3 font-semibold">{grouped.low.length}</div>
        </div>
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          <div className="font-semibold">{zh ? "需要你确认" : "Needs Approval"}</div>
          <p className="mt-2">{zh ? "这个操作可能通知他人、修改重要信息或提交一个阶段。请确认后再执行。" : "This may notify others, modify important data, or complete a section. Approve before running."}</p>
          <div className="mt-3 font-semibold">{grouped.medium.length}</div>
        </div>
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
          <div className="font-semibold">{zh ? "必须你本人手动完成" : "Manual Only"}</div>
          <p className="mt-2">{zh ? "这是高风险操作。ApplyPilot 不会自动执行。请你在学校官网页面亲自完成。" : "ApplyPilot will not automate high-risk actions. Complete them yourself on the official portal."}</p>
          <div className="mt-3 font-semibold">{grouped.blocked.length}</div>
        </div>
      </div>

      {session && (
        <div className="mt-5 rounded-2xl border border-line bg-gray-50 p-4 text-sm">
          <div className="flex flex-wrap items-center gap-3">
            <Badge tone="brand">Session #{session.id}</Badge>
            <Badge tone={session.status.includes("captcha") || session.status.includes("login") ? "warning" : "success"}>{session.status}</Badge>
            {portalUrl && <a href={portalUrl} target="_blank" className="inline-flex items-center gap-1 text-brand" rel="noreferrer">{zh ? "打开学校官网" : "Open portal"} <ExternalLink size={14} /></a>}
          </div>
          <p className="mt-3 text-muted">
            {zh ? "请你在浏览器中自行登录或完成验证码。ApplyPilot 不会保存密码，也不会绕过验证码。" : "Please log in or complete CAPTCHA yourself. ApplyPilot never stores passwords and never bypasses CAPTCHA."}
          </p>
        </div>
      )}

      <div className="mt-5 space-y-3">
        <div className="font-semibold">{zh ? "待处理动作" : "Pending Actions"}</div>
        {actions.length === 0 && (
          <div className="rounded-2xl border border-dashed border-line bg-gray-50 p-6 text-sm text-muted">
            {zh ? "还没有动作。先 Start，然后确认登录，再生成动作计划。" : "No actions yet. Start a session, confirm login, then generate the fill plan."}
          </div>
        )}
        {actions.map((action) => (
          <div key={action.id} className="rounded-2xl border border-line bg-white p-4 shadow-sm">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  {action.blocked ? <LockKeyhole size={17} className="text-rose-600" /> : action.risk_level === "medium" ? <ShieldAlert size={17} className="text-amber-600" /> : <CheckCircle2 size={17} className="text-emerald-600" />}
                  <div className="font-semibold">{action.target_label || action.action_type}</div>
                  <Badge tone={riskTone(action.risk_level)}>{action.risk_level}</Badge>
                  <Badge tone={action.status === "executed" || action.status === "user_completed" ? "success" : action.status === "blocked" || action.status === "rejected" ? "danger" : "neutral"}>{action.status}</Badge>
                </div>
                <p className="mt-2 text-sm text-muted">{action.description || action.reason}</p>
                <div className="mt-3 grid gap-2 text-xs text-muted md:grid-cols-3">
                  <div><span className="font-semibold text-ink">{zh ? "建议值" : "Proposed"}:</span> {valuePreview(action.proposed_value)}</div>
                  <div><span className="font-semibold text-ink">{zh ? "Selector" : "Selector"}:</span> {action.target_selector || "--"}</div>
                  <div><span className="font-semibold text-ink">{zh ? "原因" : "Reason"}:</span> {action.reason || "--"}</div>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 lg:justify-end">
                {!action.blocked && action.risk_level === "low" && action.status === "pending" && <Button disabled={loading !== null} onClick={() => autoRun(action)}>{zh ? "自动执行" : "Auto-run"}</Button>}
                {!action.blocked && action.risk_level === "medium" && action.status === "pending" && <Button disabled={loading !== null} onClick={() => approveAndRun(action)}>{zh ? "批准并执行" : "Approve & Run"}</Button>}
                {!action.blocked && action.risk_level === "medium" && action.status === "pending" && <button disabled={loading !== null} onClick={() => setResult({ message: zh ? "请在学校官网手动编辑该项，或后续版本在这里编辑 proposed value。" : "Edit this field manually on the portal, or edit proposed values here in a later sprint." })} className="rounded-xl border border-line bg-white px-3 py-2 text-sm font-semibold">{zh ? "编辑" : "Edit"}</button>}
                {!action.blocked && action.status === "pending" && <button disabled={loading !== null} onClick={() => reject(action)} className="rounded-xl border border-line bg-white px-3 py-2 text-sm font-semibold text-rose-600">{zh ? "拒绝" : "Reject"}</button>}
                {(action.blocked || action.risk_level === "high") && portalUrl && <a href={portalUrl} target="_blank" rel="noreferrer" className="rounded-xl border border-line bg-white px-3 py-2 text-sm font-semibold">{zh ? "手动打开" : "Open portal manually"}</a>}
                {(action.blocked || action.risk_level === "high") && <button disabled={loading !== null || action.status === "user_completed"} onClick={() => manual(action)} className="rounded-xl bg-ink px-3 py-2 text-sm font-semibold text-white disabled:bg-gray-300">{zh ? "我已手动完成" : "I completed manually"}</button>}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-5 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
        {zh
          ? "检测到最终提交或付款时，ApplyPilot 会停止自动化。请你本人检查所有信息后，在学校官网页面手动提交或付款。"
          : "When final submit or payment is detected, ApplyPilot stops automation. Review all information yourself and submit or pay manually on the official portal."}
      </div>

      <ActionResult locale={locale} title={zh ? "Portal Assistant 反馈" : "Portal Assistant Result"} data={result} error={error} />
    </Card>
  );
}
