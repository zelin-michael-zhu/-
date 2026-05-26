import Link from "next/link";
import { Program } from "@/lib/types";
import { tValue } from "@/lib/display";
import { Card } from "../common/Card";
import { Badge } from "../common/Badge";

export function ProgramMatchPreview({ locale, programs }: { locale: string; programs: Program[] }) {
  return <Card className="p-5"><div className="flex items-center justify-between"><h3 className="font-semibold">{locale === "zh" ? "Top 项目匹配" : "Top Program Matches"}</h3><Link className="text-sm font-semibold text-brand" href={`/${locale}/matches`}>{locale === "zh" ? "查看全部" : "View all"}</Link></div><div className="mt-4 space-y-3">{programs.slice(0, 4).map((p, i) => <Link href={`/${locale}/programs/${p.id}`} key={p.id} className="flex items-center justify-between rounded-xl border border-line p-3"><div><div className="text-sm font-semibold">{p.program_name}</div><div className="text-xs text-muted">{tValue(p.country, locale)} · {tValue(p.field, locale)}</div></div><Badge tone={i < 2 ? "success" : "brand"}>{90 - i * 4}</Badge></Link>)}</div></Card>;
}
