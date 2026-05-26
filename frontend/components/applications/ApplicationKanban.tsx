import { ApplicationCard } from "./ApplicationCard";

export function ApplicationKanban({ locale }: { locale: string }) {
  const cols = locale === "zh" ? ["未开始", "进行中", "已提交", "面试", "Offer", "拒信"] : ["Not Started", "In Progress", "Submitted", "Interview", "Offer", "Rejected"];
  return <div className="grid gap-4 xl:grid-cols-6">{cols.map((c, i) => <div key={c} className="rounded-2xl border border-line bg-white/70 p-3"><h3 className="mb-3 text-sm font-semibold">{c}</h3>{i < 4 && <ApplicationCard locale={locale} title={["HKU MSc Business Analytics", "NUS MSc Business Analytics", "UCL MSc Management", "CUHK MSc Finance"][i]} deadline={["Dec 01", "Nov 30", "Mar 31", "Jan 15"][i]} />}</div>)}</div>;
}
