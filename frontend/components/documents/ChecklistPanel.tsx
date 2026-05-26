import { Card } from "../common/Card";

export function ChecklistPanel({ locale }: { locale: string }) {
  const items = locale === "zh" ? ["简历", "个人陈述", "成绩单", "雅思", "两封推荐信"] : ["CV", "Personal Statement", "Transcript", "IELTS", "Two Recommendation Letters"];
  return <Card className="p-5"><h3 className="font-semibold">{locale === "zh" ? "项目材料清单" : "Application Checklist"}</h3><div className="mt-4 space-y-2">{items.map((x) => <label key={x} className="flex gap-3 text-sm"><input type="checkbox" className="accent-brand" />{x}</label>)}</div></Card>;
}
