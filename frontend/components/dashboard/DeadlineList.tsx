import { Card } from "../common/Card";
import { Badge } from "../common/Badge";

export function DeadlineList({ locale }: { locale: string }) {
  const items = ["NUS MSc Business Analytics", "HKU MSc Business Analytics", "CUHK MSc Finance"];
  return <Card className="p-5"><h3 className="font-semibold">{locale === "zh" ? "即将截止" : "Upcoming Deadlines"}</h3><div className="mt-4 space-y-3">{items.map((x, i) => <div key={x} className="flex items-center justify-between rounded-xl bg-gray-50 p-3 text-sm"><span>{x}</span><Badge tone={i === 0 ? "warning" : "neutral"}>{i === 0 ? "Nov 30" : "Dec 01"}</Badge></div>)}</div></Card>;
}
