"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/common/Card";
import { Badge } from "@/components/common/Badge";
import { getDefaultApplicant, getEmails } from "@/lib/api";
import { tValue } from "@/lib/display";

type EmailItem = {
  id: number;
  sender: string;
  subject: string;
  body_preview?: string;
  category: string;
  ai_summary?: string;
  suggested_action?: string;
};

export default function EmailTracker({ params }: { params: Promise<{ locale: string }> }) {
  const [locale, setLocale] = useState("en");
  const zh = locale === "zh";
  const [emails, setEmails] = useState<EmailItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    params.then(({ locale }) => setLocale(locale));
  }, [params]);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const applicant = await getDefaultApplicant();
        setEmails(await getEmails(applicant.id) as EmailItem[]);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return <AppShell locale={locale}><h1 className="mb-6 text-3xl font-bold">{zh ? "邮箱追踪" : "Email Tracker"}</h1>{loading && <Card className="p-5 text-sm text-muted">{zh ? "正在加载邮件..." : "Loading emails..."}</Card>}{error && <Card className="p-5 text-sm text-rose-700">{error}</Card>}<div className="grid gap-4">{emails.map((email) => <Card key={email.id} className="p-5"><div className="flex items-center justify-between gap-4"><div><h3 className="font-semibold">{email.subject}</h3><p className="mt-1 text-xs text-muted">{email.sender}</p><p className="mt-2 text-sm text-muted">{email.ai_summary || email.body_preview || (zh ? "MVP 使用 mock 邮件分类和建议动作，不连接真实邮箱。" : "Mock email category and suggested action. No real mailbox authorization in MVP.")}</p>{email.suggested_action && <p className="mt-2 text-sm font-medium text-ink">{email.suggested_action}</p>}</div><Badge tone={email.category === "Urgent" ? "danger" : email.category === "Updates" ? "brand" : "success"}>{tValue(email.category, locale)}</Badge></div></Card>)}</div></AppShell>;
}
