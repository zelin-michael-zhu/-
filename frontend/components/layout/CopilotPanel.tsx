import { Sparkles } from "lucide-react";
import { Card } from "../common/Card";

export function CopilotPanel({ locale }: { locale: string }) {
  const zh = locale === "zh";
  return (
    <Card className="p-5">
      <div className="flex items-center gap-2 font-semibold"><Sparkles size={18} className="text-brand" /> AI Copilot</div>
      <p className="mt-3 text-sm leading-6 text-muted">{zh ? "我会帮你发现材料缺口、提醒截止日期，并在高风险动作前等待你的确认。" : "I help surface gaps, deadlines, and recommendations. High-risk actions always wait for your approval."}</p>
      <div className="mt-5 space-y-3 text-sm">
        {(zh ? ["先完成 NUS 面试回复", "为 HKU 补充成绩单", "把 SOP 调整为数据分析方向"] : ["Reply to NUS interview", "Upload HKU transcript", "Tailor SOP for analytics"]).map((x) => <div key={x} className="rounded-xl border border-line bg-gray-50 p-3">{x}</div>)}
      </div>
    </Card>
  );
}
