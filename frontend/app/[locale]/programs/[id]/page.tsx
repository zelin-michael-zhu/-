import { AppShell } from "@/components/layout/AppShell";
import { ProgramDetailPanel } from "@/components/programs/ProgramDetailPanel";
import { getProgram } from "@/lib/api";

export default async function ProgramDetail({ params }: { params: Promise<{ locale: string; id: string }> }) {
  const { locale, id } = await params;
  const program = await getProgram(id);
  return <AppShell locale={locale} copilot={false}>{program && <ProgramDetailPanel program={program} locale={locale} />}</AppShell>;
}
