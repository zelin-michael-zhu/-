import { Program } from "@/lib/types";
import { tValue } from "@/lib/display";
import { Card } from "../common/Card";
import { Badge } from "../common/Badge";

export function ProgramDetailPanel({ program, locale }: { program: Program; locale: string }) {
  const zh = locale === "zh";
  const labels = {
    overview: zh ? "概览" : "Overview",
    requirements: zh ? "申请要求" : "Requirements",
    deadlines: zh ? "截止日期" : "Deadlines",
    tuition: zh ? "学费" : "Tuition",
    documents: zh ? "材料" : "Documents",
    source: zh ? "来源链接" : "Source URLs",
    raw: zh ? "原始文本快照" : "Raw text snapshot",
    noRaw: zh ? "当前 demo fallback 没有原始文本快照。" : "No raw snapshot in demo fallback."
  };
  return (
    <div className="space-y-6">
      <Card className="p-6">
        <Badge tone="warning">{locale === "zh" ? "申请前必须核对官网" : "Verify with official website before applying"}</Badge>
        <h1 className="mt-4 text-3xl font-bold">{program.program_name}</h1>
        <p className="mt-2 text-muted">{program.university_name} · {tValue(program.country, locale)} · {tValue(program.field, locale)}</p>
        <p className="mt-4 text-sm leading-6 text-muted">{program.description || "Demo seeded program for local MVP browsing. Auto-extracted data, please verify with official website."}</p>
      </Card>
      <div className="grid gap-6 lg:grid-cols-2">
        {[
          [labels.overview, `${program.degree_type || "MSc"} · ${tValue(program.duration || "1 year", locale)} · ${tValue("Full-time", locale)}`],
          [labels.requirements, `IELTS ${program.ielts_requirement || tValue("TBC", locale)} · TOEFL ${program.toefl_requirement || tValue("TBC", locale)} · GRE ${program.gre_required ? tValue("Required", locale) : tValue("Not required", locale)}`],
          [labels.deadlines, program.application_deadline || tValue("TBC", locale)],
          [labels.tuition, `${program.tuition_currency || ""} ${program.tuition_amount?.toLocaleString() || tValue("TBC", locale)}`],
          [labels.documents, zh ? "简历、个人陈述、成绩单、雅思、推荐信" : "CV, Personal Statement, Transcript, IELTS, Recommendation Letters"],
          [labels.source, program.source_url || tValue("TBC", locale)]
        ].map(([title, body]) => <Card key={title} className="p-5"><h3 className="font-semibold">{title}</h3><p className="mt-3 break-words text-sm leading-6 text-muted">{body}</p></Card>)}
      </div>
      <Card className="p-5"><h3 className="font-semibold">{labels.raw}</h3><pre className="mt-3 max-h-72 overflow-auto whitespace-pre-wrap rounded-xl bg-gray-50 p-4 text-xs text-muted">{program.raw_text_snapshot || labels.noRaw}</pre></Card>
    </div>
  );
}
