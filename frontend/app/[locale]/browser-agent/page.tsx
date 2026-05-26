import { AppShell } from "@/components/layout/AppShell";
import { BrowserAgentConsole } from "@/components/browser-agent/BrowserAgentConsole";
import { BrowserExecutorPanel } from "@/components/browser-agent/BrowserExecutorPanel";
import { PortalApprovalGatePanel } from "@/components/browser-agent/PortalApprovalGatePanel";

export default async function BrowserAgent({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  return <AppShell locale={locale} copilot={false}><h1 className="mb-6 text-3xl font-bold">{locale === "zh" ? "浏览器助手" : "Browser Agent"}</h1><div className="space-y-6"><PortalApprovalGatePanel locale={locale} /><BrowserExecutorPanel locale={locale} /><BrowserAgentConsole locale={locale} /></div></AppShell>;
}
