import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/common/Card";

export default async function InterviewPrep({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const sections = locale === "zh" ? ["面试题库", "自我介绍", "为什么这个项目", "为什么这所大学", "模拟面试笔记", "反馈"] : ["Interview question bank", "Self introduction", "Why this program", "Why this university", "Mock interview notes", "Feedback"];
  return <AppShell locale={locale}><h1 className="mb-6 text-3xl font-bold">{locale === "zh" ? "面试准备" : "Interview Prep"}</h1><div className="grid gap-4 md:grid-cols-2">{sections.map((s) => <Card key={s} className="p-5"><h3 className="font-semibold">{s}</h3><p className="mt-3 text-sm leading-6 text-muted">Tell me about yourself. Describe a business analytics project. Explain your career plan and program fit.</p></Card>)}</div></AppShell>;
}
