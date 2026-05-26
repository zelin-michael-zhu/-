import { Card } from "../common/Card";
import { DocumentStatusBadge } from "./DocumentStatusBadge";

export function DocumentCard({ name, status, locale = "en" }: { name: string; status: string; locale?: string }) {
  return <Card className="p-4"><div className="flex items-center justify-between"><div className="font-semibold">{name}</div><DocumentStatusBadge status={status} locale={locale} /></div><p className="mt-2 text-sm text-muted">{locale === "zh" ? "用于多个已选择申请项目。" : "Used across selected applications."}</p></Card>;
}
