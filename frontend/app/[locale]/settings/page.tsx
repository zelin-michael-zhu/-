import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/common/Card";

export default async function Settings({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const zh = locale === "zh";
  const items = zh ? ["个人资料", "语言", "隐私", "邮箱授权 Mock", "AI 权限", "通知设置"] : ["Profile", "Language", "Privacy", "Email authorization mock", "AI permissions", "Notification settings"];
  return <AppShell locale={locale}><h1 className="mb-6 text-3xl font-bold">{zh ? "设置" : "Settings"}</h1><div className="grid gap-4 md:grid-cols-2">{items.map((s) => <Card key={s} className="p-5"><div className="flex items-center justify-between"><div><h3 className="font-semibold">{s}</h3><p className="mt-2 text-sm text-muted">{zh ? "不保存真实密码；高风险 AI 动作必须人工确认。" : "No real passwords are stored. High-risk AI actions require approval."}</p></div><input type="checkbox" defaultChecked className="h-5 w-5 accent-brand" /></div></Card>)}</div></AppShell>;
}
