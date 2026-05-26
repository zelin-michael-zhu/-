import { AppShell } from "@/components/layout/AppShell";
import ProgramDiscoveryClient from "./ProgramDiscoveryClient";

export default async function ProgramDiscovery({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  return (
    <AppShell locale={locale}>
      <ProgramDiscoveryClient locale={locale} />
    </AppShell>
  );
}
