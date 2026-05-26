"use client";

import { useState } from "react";
import { Badge } from "../common/Badge";
import { Card } from "../common/Card";
import { ChevronDown, ChevronUp, ExternalLink, Eye, EyeOff } from "lucide-react";

type DiscoveryProgram = {
  id: number;
  program_name: string;
  university_name?: string | null;
  degree_type?: string | null;
  field?: string | null;
  duration?: string | null;
  tuition_amount?: number | null;
  tuition_currency?: string | null;
  application_deadline?: string | null;
  deadline_note?: string | null;
  intake?: string | null;
  ielts_requirement?: string | null;
  toefl_requirement?: string | null;
  gre_required?: boolean | null;
  gmat_required?: boolean | null;
  work_experience_required?: boolean | null;
  program_url?: string | null;
  source_url?: string | null;
  description_preview?: string | null;
  extraction_confidence?: number | null;
  review_status?: string | null;
  country?: string | null;
  city?: string | null;
  faculty?: string | null;
  study_mode?: string | null;
};

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export function ProgramResultCard({
  program,
  locale,
}: {
  program: DiscoveryProgram;
  locale: string;
}) {
  const zh = locale === "zh";
  const [expanded, setExpanded] = useState(false);
  const [added, setAdded] = useState(false);
  const [reviewed, setReviewed] = useState(program.review_status === "reviewed");

  const confidence = program.extraction_confidence ?? 0;
  const confidencePct = Math.round(confidence * 100);

  async function handleAddToDatabase() {
    setAdded(true);
  }

  async function handleMarkReviewed() {
    try {
      await fetch(`${API}/programs/${program.id}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ review_status: "reviewed" }),
      });
      setReviewed(true);
    } catch {}
  }

  return (
    <Card className="overflow-hidden">
      <div className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <h4 className="font-semibold text-ink truncate">{program.program_name}</h4>
            <p className="mt-0.5 text-sm text-muted">
              {program.university_name || program.country}
              {program.faculty ? ` · ${program.faculty}` : ""}
            </p>
          </div>
          <Badge tone={confidence >= 0.75 ? "brand" : "warning"}>
            {confidencePct}%
          </Badge>
        </div>

        <div className="mt-3 flex flex-wrap gap-2 text-xs text-muted">
          {program.degree_type && (
            <span className="rounded-lg bg-gray-100 px-2 py-1">{program.degree_type}</span>
          )}
          {program.field && (
            <span className="rounded-lg bg-gray-100 px-2 py-1">{program.field}</span>
          )}
          {program.duration && (
            <span className="rounded-lg bg-gray-100 px-2 py-1">{program.duration}</span>
          )}
          {program.study_mode && (
            <span className="rounded-lg bg-gray-100 px-2 py-1">{program.study_mode}</span>
          )}
        </div>

        <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
          {program.tuition_amount != null && (
            <div>
              <span className="text-muted">{zh ? "学费：" : "Tuition: "}</span>
              <span className="font-medium">
                {program.tuition_currency || ""} {program.tuition_amount.toLocaleString()}
              </span>
            </div>
          )}
          {program.application_deadline && (
            <div>
              <span className="text-muted">{zh ? "截止日期：" : "Deadline: "}</span>
              <span className="font-medium">{program.application_deadline}</span>
            </div>
          )}
          {program.ielts_requirement && (
            <div>
              <span className="text-muted">IELTS: </span>
              <span className="font-medium">{program.ielts_requirement}</span>
            </div>
          )}
          {program.toefl_requirement && (
            <div>
              <span className="text-muted">TOEFL: </span>
              <span className="font-medium">{program.toefl_requirement}</span>
            </div>
          )}
        </div>

        {program.description_preview && (
          <p className="mt-3 line-clamp-2 text-xs text-muted">{program.description_preview}</p>
        )}

        {expanded && (
          <div className="mt-4 border-t border-line pt-3 text-xs text-muted space-y-2">
            {program.intake && <p>{zh ? "入学季：" : "Intake: "}{program.intake}</p>}
            {program.deadline_note && <p>{zh ? "截止说明：" : "Deadline note: "}{program.deadline_note}</p>}
            <p>
              GRE: {program.gre_required ? (zh ? "需要" : "Required") : (zh ? "不需要" : "Not required")}
              {" · "}
              GMAT: {program.gmat_required ? (zh ? "需要" : "Required") : (zh ? "不需要" : "Not required")}
            </p>
            <p>
              {zh ? "工作经验：" : "Work experience: "}
              {program.work_experience_required ? (zh ? "需要" : "Required") : (zh ? "不需要" : "Not required")}
            </p>
            {program.source_url && <p className="break-all">{zh ? "来源：" : "Source: "}{program.source_url}</p>}
          </div>
        )}

        <div className="mt-4 flex flex-wrap items-center gap-2">
          {program.program_url && (
            <a
              href={program.program_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 rounded-lg border border-line px-3 py-1.5 text-xs font-semibold hover:bg-gray-50"
            >
              <ExternalLink size={12} />
              {zh ? "查看来源" : "View source"}
            </a>
          )}
          {program.source_url && program.source_url !== program.program_url && (
            <a
              href={program.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 rounded-lg border border-line px-3 py-1.5 text-xs font-semibold hover:bg-gray-50"
            >
              <ExternalLink size={12} />
              {zh ? "原始页面" : "Raw page"}
            </a>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="inline-flex items-center gap-1 rounded-lg border border-line px-3 py-1.5 text-xs font-semibold hover:bg-gray-50"
          >
            {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            {zh ? "高级详情" : "Advanced details"}
          </button>
          <div className="flex-1" />
          {!added && (
            <button
              onClick={handleAddToDatabase}
              className="rounded-lg bg-brand px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700"
            >
              {zh ? "加入项目库" : "Add to Database"}
            </button>
          )}
          {added && (
            <span className="text-xs text-emerald-600 font-medium">
              {zh ? "已加入" : "Added"}
            </span>
          )}
          {!reviewed && (
            <button
              onClick={handleMarkReviewed}
              className="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700"
            >
              {zh ? "标记已审核" : "Mark reviewed"}
            </button>
          )}
          {reviewed && (
            <span className="text-xs text-emerald-600 font-medium">
              {zh ? "已审核" : "Reviewed"}
            </span>
          )}
        </div>
      </div>
    </Card>
  );
}
