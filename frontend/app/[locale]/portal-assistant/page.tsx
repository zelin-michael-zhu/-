import { PortalApprovalGatePanel } from "@/components/browser-agent/PortalApprovalGatePanel";
import { AppShell } from "@/components/layout/AppShell";

export default async function PortalAssistant({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  return (
    <AppShell locale={locale} copilot={false}>
      <h1 className="mb-6 text-3xl font-bold">{locale === "zh" ? "Portal Assistant" : "Portal Assistant"}</h1>
      <PortalApprovalGatePanel locale={locale} />
    </AppShell>
  );
}
