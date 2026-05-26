import Link from "next/link";
import { ArrowRight, Bot, Database, ShieldCheck, Sparkles } from "lucide-react";
import { getDictionary } from "@/lib/i18n";
import { Card } from "@/components/common/Card";

export default async function Landing({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const dict = getDictionary(locale);
  const zh = locale === "zh";
  return (
    <main className="min-h-screen bg-[#F7F8FA] px-6 py-8">
      <nav className="mx-auto flex max-w-6xl items-center justify-between"><div className="text-xl font-bold">ApplyPilot</div><Link href={`/${locale}/dashboard`} className="rounded-xl bg-ink px-4 py-2 text-sm font-semibold text-white">{dict.landing.cta}</Link></nav>
      <section className="mx-auto grid max-w-6xl gap-10 py-20 lg:grid-cols-[1fr_520px]">
        <div><div className="mb-5 inline-flex rounded-full border border-line bg-white px-3 py-1 text-sm text-muted">Calm Premium Dashboard · AI Copilot-assisted</div><h1 className="text-5xl font-bold tracking-tight">{dict.landing.title}</h1><p className="mt-5 max-w-xl text-lg leading-8 text-muted">{dict.landing.subtitle}</p><Link href={`/${locale}/dashboard`} className="mt-8 inline-flex items-center gap-2 rounded-xl bg-brand px-5 py-3 font-semibold text-white">{dict.landing.cta}<ArrowRight size={18} /></Link></div>
        <Card className="p-5"><div className="grid gap-4"><div className="rounded-2xl bg-ink p-5 text-white"><div className="text-sm opacity-70">Profile Strength</div><div className="mt-3 text-4xl font-bold">82%</div></div><div className="grid grid-cols-2 gap-4"><div className="rounded-2xl bg-gray-50 p-4"><Database className="text-brand" /><div className="mt-3 font-semibold">8 Programs</div></div><div className="rounded-2xl bg-gray-50 p-4"><Sparkles className="text-brand" /><div className="mt-3 font-semibold">6 Matches</div></div></div><div className="rounded-2xl border border-line p-4 text-sm text-muted">NUS interview invitation · HKU missing transcript request</div></div></Card>
      </section>
      <section className="mx-auto grid max-w-6xl gap-5 pb-20 md:grid-cols-4">{[[Database, zh ? "项目数据库" : "Program Match"], [Sparkles, zh ? "申请流程" : "Application Pipeline"], [Bot, zh ? "浏览器助手" : "Browser Agent"], [ShieldCheck, zh ? "安全与隐私" : "Security & Privacy"]].map(([Icon, title]: any) => <Card key={title} className="p-5"><Icon className="text-brand" /><h3 className="mt-4 font-bold">{title}</h3><p className="mt-2 text-sm text-muted">{zh ? "以工作流为中心，关键动作人工确认。" : "Workflow-driven with human approval for sensitive actions."}</p></Card>)}</section>
    </main>
  );
}
