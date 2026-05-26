import { AppShell } from "@/components/layout/AppShell";
import { DashboardClient } from "@/components/dashboard/DashboardClient";

export default async function Dashboard({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  return <AppShell locale={locale}><DashboardClient locale={locale} /></AppShell>;
}
