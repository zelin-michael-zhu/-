import { Card } from "../common/Card";

export function GpaConverterCard({ locale, value, scale, converted }: { locale: string; value?: number | null; scale?: number | null; converted?: number | null }) {
  return <Card className="p-5"><h3 className="font-semibold">GPA</h3><div className="mt-4 text-3xl font-bold">{converted?.toFixed(2) || "--"} / 4.0</div><p className="mt-2 text-sm text-muted">{value ?? "--"} / {scale ?? "--"}</p><p className="mt-3 text-sm text-muted">{locale === "zh" ? "这是系统估算，最终评估以各大学官方审核为准。" : "This is an estimate. Final evaluation depends on each university."}</p></Card>;
}
