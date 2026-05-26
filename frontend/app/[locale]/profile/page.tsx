import { AppShell } from "@/components/layout/AppShell";
import { ProfileClient } from "@/components/profile/ProfileClient";

export default async function Profile({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const zh = locale === "zh";
  return <AppShell locale={locale}><h1 className="mb-6 text-3xl font-bold">{zh ? "我的背景" : "My Profile"}</h1><ProfileClient locale={locale} /></AppShell>;
}
