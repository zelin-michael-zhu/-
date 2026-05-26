"use client";

import { CheckCircle, Circle, Loader2, XCircle } from "lucide-react";

type Step = {
  step: string;
  status: "pending" | "completed" | "failed";
};

const STEP_LABELS_EN: Record<string, string> = {
  "Checking official source": "Checking official source",
  "Reading robots.txt": "Reading robots.txt",
  "Discovering program links": "Discovering program links",
  "Fetching allowed pages": "Fetching allowed pages",
  "Extracting program details": "Extracting program details",
  "Preparing results": "Preparing results",
};

const STEP_LABELS_ZH: Record<string, string> = {
  "Checking official source": "检查官方来源",
  "Reading robots.txt": "读取 robots.txt",
  "Discovering program links": "发现项目链接",
  "Fetching allowed pages": "抓取允许页面",
  "Extracting program details": "抽取项目详情",
  "Preparing results": "准备结果",
};

function StepIcon({ status }: { status: Step["status"] }) {
  if (status === "completed") return <CheckCircle size={18} className="text-emerald-500" />;
  if (status === "failed") return <XCircle size={18} className="text-rose-500" />;
  return <Circle size={18} className="text-gray-300" />;
}

export function ProgressTimeline({ locale, steps }: { locale: string; steps: Step[] }) {
  const zh = locale === "zh";
  const labels = zh ? STEP_LABELS_ZH : STEP_LABELS_EN;

  if (!steps || steps.length === 0) return null;

  return (
    <div className="space-y-1">
      {steps.map((s, i) => (
        <div key={i} className="flex items-center gap-3 py-1.5">
          <StepIcon status={s.status} />
          <span
            className={`text-sm ${
              s.status === "completed"
                ? "text-ink font-medium"
                : s.status === "failed"
                  ? "text-rose-600"
                  : "text-muted"
            }`}
          >
            {labels[s.step] || s.step}
          </span>
        </div>
      ))}
    </div>
  );
}
