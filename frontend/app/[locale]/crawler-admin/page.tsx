import { AppShell } from "@/components/layout/AppShell";
import { CrawlerControlPanel } from "@/components/crawler/CrawlerControlPanel";
import { CrawlerRunTable } from "@/components/crawler/CrawlerRunTable";
import { ReviewQueuePanel } from "@/components/crawler/ReviewQueuePanel";

export default async function CrawlerAdmin({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  return (
    <AppShell locale={locale}>
      <h1 className="mb-2 text-2xl font-bold text-ink">
        {locale === "zh" ? "爬虫管理后台" : "Crawler Admin"}
      </h1>
      <p className="mb-6 text-sm text-muted">
        {locale === "zh"
          ? "开发者工具。遵守 robots.txt 和速率限制；不登录、不绕过验证码、不付款、不最终提交。"
          : "Developer tools. Robots.txt, rate limits, no login, no CAPTCHA bypass, no payment, no final submit."}
      </p>
      <div className="space-y-6">
        <CrawlerControlPanel locale={locale} />
        <CrawlerRunTable locale={locale} />
        <ReviewQueuePanel locale={locale} />
      </div>
    </AppShell>
  );
}
