import Link from "next/link";
import { BarChart3, Bot, BriefcaseBusiness, ClipboardCheck, Database, FileText, GraduationCap, Inbox, LayoutDashboard, Search, Settings, ShieldCheck, Sparkles, UserRound, Wrench } from "lucide-react";

const items = [
  ["dashboard", LayoutDashboard, "dashboard"],
  ["programs", Database, "programs"],
  ["profile", UserRound, "profile"],
  ["programDiscovery", Search, "program-discovery"],
  ["matches", Sparkles, "matches"],
  ["documents", FileText, "documents"],
  ["applications", ClipboardCheck, "applications"],
  ["browserAgent", Bot, "browser-agent"],
  ["portalAssistant", ShieldCheck, "portal-assistant"],
  ["emailTracker", Inbox, "email-tracker"],
  ["interviewPrep", GraduationCap, "interview-prep"],
  ["crawlerAdmin", Wrench, "crawler-admin"],
  ["settings", Settings, "settings"]
] as const;

export function Sidebar({ locale, dict }: { locale: string; dict: any }) {
  return (
    <aside className="fixed left-0 top-0 hidden h-screen w-72 border-r border-line bg-white/90 px-4 py-5 backdrop-blur lg:block">
      <Link href={`/${locale}`} className="mb-7 flex items-center gap-3 px-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-ink text-white"><BriefcaseBusiness size={20} /></div>
        <div><div className="font-bold">ApplyPilot</div><div className="text-xs text-muted">Graduate Application OS</div></div>
      </Link>
      <nav className="space-y-1">
        {items.map(([key, Icon, href]) => (
          <Link key={key} href={`/${locale}/${href}`} className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50">
            <Icon size={18} /> {dict.nav[key]}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
