"use client";

import Link from "next/link";
import { ExternalLink } from "lucide-react";
import { useState } from "react";
import { addApplication, getDefaultApplicant } from "@/lib/api";
import { Program } from "@/lib/types";
import { tValue } from "@/lib/display";
import { Badge } from "../common/Badge";
import { Card } from "../common/Card";

export function ProgramCard({ program, locale }: { program: Program; locale: string }) {
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const labels = locale === "zh" ? {
    country: "国家/地区",
    field: "方向",
    deadline: "截止日期",
    tuition: "学费",
    language: "语言",
    tests: "标化",
    confidence: "置信度",
    degree: "学位",
    greWaived: "GRE 免交",
    gmatWaived: "GMAT 免交"
  } : {
    country: "Country",
    field: "Field",
    deadline: "Deadline",
    tuition: "Tuition",
    language: "Language",
    tests: "Tests",
    confidence: "Confidence",
    degree: "Degree",
    greWaived: "GRE waived",
    gmatWaived: "GMAT waived"
  };
  async function add() {
    setAdding(true);
    setError(null);
    try {
      const applicant = await getDefaultApplicant();
      await addApplication(applicant.id, program.id);
      setAdded(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setAdding(false);
    }
  }
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-muted">{program.university_name}</p>
          <h3 className="mt-1 text-lg font-bold">{program.program_name}</h3>
        </div>
        <Badge tone={program.review_status === "auto_extracted" ? "brand" : "warning"}>{program.review_status}</Badge>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-muted md:grid-cols-4">
        <div><b className="text-ink">{tValue(program.country, locale)}</b><br />{labels.country}</div>
        <div><b className="text-ink">{tValue(program.field, locale)}</b><br />{labels.field}</div>
        <div><b className="text-ink">{program.application_deadline || tValue("TBC", locale)}</b><br />{labels.deadline}</div>
        <div><b className="text-ink">{program.tuition_currency} {program.tuition_amount?.toLocaleString()}</b><br />{labels.tuition}</div>
        <div><b className="text-ink">IELTS {program.ielts_requirement}</b><br />{labels.language}</div>
        <div><b className="text-ink">{program.gre_required ? "GRE" : labels.greWaived} / {program.gmat_required ? "GMAT" : labels.gmatWaived}</b><br />{labels.tests}</div>
        <div><b className="text-ink">{Math.round((program.extraction_confidence || 0) * 100)}%</b><br />{labels.confidence}</div>
        <div><b className="text-ink">{program.degree_type}</b><br />{labels.degree}</div>
      </div>
      <div className="mt-5 flex items-center justify-between border-t border-line pt-4">
        <div>
          <p className="text-xs text-amber-700">{locale === "zh" ? "自动抽取数据，请核对官网。" : "Auto-extracted data, please verify with official website."}</p>
          {error && <p className="mt-1 text-xs text-rose-700">{error}</p>}
        </div>
        <div className="flex flex-wrap items-center justify-end gap-3">
          <button onClick={add} disabled={adding || added} className="rounded-xl bg-ink px-3 py-2 text-sm font-semibold text-white disabled:bg-emerald-600">
            {added ? (locale === "zh" ? "已添加" : "Added") : adding ? (locale === "zh" ? "添加中" : "Adding") : (locale === "zh" ? "加入申请" : "Add application")}
          </button>
          <Link className="inline-flex items-center gap-2 text-sm font-semibold text-brand" href={`/${locale}/programs/${program.id}`}>{locale === "zh" ? "查看详情" : "View details"} <ExternalLink size={15} /></Link>
        </div>
      </div>
    </Card>
  );
}
