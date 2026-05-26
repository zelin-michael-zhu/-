import type { Locale } from "./types";

const zhMap: Record<string, string> = {
  "Hong Kong": "中国香港",
  Singapore: "新加坡",
  "United Kingdom": "英国",
  Australia: "澳大利亚",
  "Business Analytics": "商业分析",
  Finance: "金融",
  FinTech: "金融科技",
  "Data Science": "数据科学",
  Management: "管理学",
  Marketing: "市场营销",
  "auto_extracted": "自动抽取",
  "needs_review": "待审核",
  reviewed: "已审核",
  rejected: "已拒绝",
  ready: "已就绪",
  draft: "草稿",
  missing: "缺失",
  submitted: "已提交",
  "Not Started": "未开始",
  "In Progress": "进行中",
  Submitted: "已提交",
  Interview: "面试",
  Offer: "录取",
  Rejected: "拒信",
  "Strong Target": "强目标",
  Target: "目标",
  Safety: "保底",
  Reach: "冲刺",
  "Not Recommended": "不推荐",
  Urgent: "紧急",
  Updates: "动态更新",
  "No Action Needed": "无需操作",
  "Full-time": "全日制",
  "1 year": "1 年",
  Required: "需要",
  "Not required": "不需要",
  "TBC": "待确认"
};

export function tValue(value: string | undefined | null, locale: string): string {
  if (!value) return locale === "zh" ? "待确认" : "TBC";
  return locale === "zh" ? zhMap[value] || value : value;
}

export function documentName(name: string, locale: string): string {
  if (locale !== "zh") return name;
  const map: Record<string, string> = {
    CV: "简历",
    "Personal Statement": "个人陈述",
    Transcript: "成绩单",
    "Degree Certificate": "学位证明",
    IELTS: "雅思",
    TOEFL: "托福",
    GRE: "GRE",
    GMAT: "GMAT",
    "Recommendation Letter 1": "推荐信 1",
    "Recommendation Letter 2": "推荐信 2",
    "Recommendation Letter": "推荐信",
    Passport: "护照",
    "Research Proposal": "研究计划",
    "Writing Sample": "写作样本",
    Portfolio: "作品集",
    Other: "其他"
  };
  return map[name] || name;
}
