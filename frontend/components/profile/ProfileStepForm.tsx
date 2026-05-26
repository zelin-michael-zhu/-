import { Card } from "../common/Card";

export function ProfileStepForm({ locale }: { locale: string }) {
  const steps = locale === "zh" ? ["教育背景", "GPA", "语言/标化", "经历", "偏好"] : ["Education", "GPA", "Test Scores", "Experiences", "Preferences"];
  return <Card className="p-6"><div className="mb-6 flex flex-wrap gap-2">{steps.map((s, i) => <span key={s} className={`rounded-full px-3 py-1 text-sm ${i === 0 ? "bg-ink text-white" : "bg-gray-100 text-muted"}`}>{s}</span>)}</div><div className="grid gap-4 md:grid-cols-2">{["Full name", "University", "Major", "Graduation year", "GPA", "IELTS"].map((x) => <label key={x} className="text-sm font-medium">{x}<input className="mt-2 w-full rounded-xl border border-line px-3 py-2 outline-none focus:border-brand" defaultValue={x === "Full name" ? "Zeklin Zhu" : x === "GPA" ? "3.62" : ""} /></label>)}</div></Card>;
}
