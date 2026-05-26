import { Card } from "../common/Card";

export function TaskList({ locale }: { locale: string }) {
  const items = locale === "zh" ? ["完成推荐人信息", "更新英文 CV", "检查 HKU 成绩单要求"] : ["Finalize recommenders", "Update English CV", "Check HKU transcript requirement"];
  return <Card className="p-5"><h3 className="font-semibold">{locale === "zh" ? "我的任务" : "My Tasks"}</h3><div className="mt-4 space-y-3">{items.map((x) => <label key={x} className="flex items-center gap-3 rounded-xl border border-line p-3 text-sm"><input type="checkbox" className="h-4 w-4 accent-brand" />{x}</label>)}</div></Card>;
}
