import { Bell, Search } from "lucide-react";
import { LanguageSwitcher } from "./LanguageSwitcher";

export function Topbar({ locale }: { locale: string }) {
  const placeholder = locale === "zh" ? "搜索项目、材料、截止日期" : "Search programs, documents, deadlines";
  return (
    <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-line bg-[#F7F8FA]/85 px-4 backdrop-blur lg:px-8">
      <div className="hidden w-96 items-center gap-2 rounded-xl border border-line bg-white px-3 py-2 text-sm text-muted md:flex"><Search size={16} /> {placeholder}</div>
      <div className="font-semibold lg:hidden">ApplyPilot</div>
      <div className="flex items-center gap-3"><LanguageSwitcher locale={locale} /><button className="rounded-xl border border-line bg-white p-2 text-muted"><Bell size={18} /></button><div className="h-9 w-9 rounded-full bg-ink text-center text-sm font-bold leading-9 text-white">ZZ</div></div>
    </header>
  );
}
