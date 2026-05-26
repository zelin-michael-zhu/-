import { Card } from "../common/Card";

export function ActionLog({ locale }: { locale: string }) {
  const logs = locale === "zh" ? ["已打开本地样例申请表", "准备填写姓名、邮箱、学校、专业、GPA", "等待人工确认", "最终提交和付款已禁用"] : ["Opened local sample form", "Prepared name, email, university, major, GPA", "Waiting for human approval", "Final submit and payment are disabled"];
  return <Card className="p-5"><h3 className="font-semibold">{locale === "zh" ? "AI 操作日志" : "AI Action Log"}</h3><div className="mt-4 space-y-3">{logs.map((x) => <div key={x} className="rounded-xl bg-gray-50 p-3 text-sm text-muted">{x}</div>)}</div></Card>;
}
