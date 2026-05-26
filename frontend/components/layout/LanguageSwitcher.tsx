"use client";
import { usePathname, useRouter } from "next/navigation";

export function LanguageSwitcher({ locale }: { locale: string }) {
  const router = useRouter();
  const pathname = usePathname();
  function change(next: string) {
    const parts = pathname.split("/");
    parts[1] = next;
    router.push(parts.join("/") || `/${next}`);
  }
  return (
    <div className="flex rounded-xl border border-line bg-white p-1 text-sm">
      {["en", "zh"].map((item) => <button key={item} onClick={() => change(item)} className={`rounded-lg px-3 py-1.5 font-medium ${locale === item ? "bg-ink text-white" : "text-muted"}`}>{item === "en" ? "English" : "中文"}</button>)}
    </div>
  );
}
