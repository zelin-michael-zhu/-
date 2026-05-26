import { Badge } from "../common/Badge";
import { tValue } from "@/lib/display";

export function DocumentStatusBadge({ status, locale = "en" }: { status: string; locale?: string }) {
  const tone = status === "ready" || status === "submitted" ? "success" : status === "draft" ? "warning" : "danger";
  return <Badge tone={tone as any}>{tValue(status, locale)}</Badge>;
}
