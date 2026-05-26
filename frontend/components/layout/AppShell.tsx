import { ReactNode } from "react";
import { getDictionary } from "@/lib/i18n";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { CopilotPanel } from "./CopilotPanel";

export function AppShell({ locale, children, copilot = true }: { locale: string; children: ReactNode; copilot?: boolean }) {
  const dict = getDictionary(locale);
  return (
    <div className="min-h-screen bg-[#F7F8FA]">
      <Sidebar locale={locale} dict={dict} />
      <main className="lg:pl-72">
        <Topbar locale={locale} />
        <div className={`grid gap-6 p-4 lg:p-8 ${copilot ? "xl:grid-cols-[minmax(0,1fr)_320px]" : ""}`}>
          <section>{children}</section>
          {copilot && <aside className="hidden xl:block"><CopilotPanel locale={locale} /></aside>}
        </div>
      </main>
    </div>
  );
}
