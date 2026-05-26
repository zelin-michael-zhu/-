import { Card } from "../common/Card";

export function ApplicationCard({ title, deadline, locale = "en" }: { title: string; deadline: string; locale?: string }) {
  return <Card className="p-4 shadow-none"><div className="font-semibold">{title}</div><p className="mt-2 text-xs text-muted">{locale === "zh" ? "截止日期" : "Deadline"} {deadline}</p><div className="mt-3 h-1.5 rounded-full bg-gray-100"><div className="h-1.5 w-2/3 rounded-full bg-brand" /></div></Card>;
}
