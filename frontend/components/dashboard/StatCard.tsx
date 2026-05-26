import { Card } from "../common/Card";

export function StatCard({ label, value, hint }: { label: string; value: string; hint: string }) {
  return <Card className="p-5"><p className="text-sm text-muted">{label}</p><div className="mt-3 text-3xl font-bold">{value}</div><p className="mt-2 text-xs text-muted">{hint}</p></Card>;
}
