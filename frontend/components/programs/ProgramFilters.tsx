import { SlidersHorizontal } from "lucide-react";

export type ProgramFilterState = {
  search: string;
  country: string;
  field: string;
  university: string;
  review_status: string;
  min_confidence: string;
};

export function ProgramFilters({ locale, filters, onChange }: { locale: string; filters: ProgramFilterState; onChange: (next: ProgramFilterState) => void }) {
  const zh = locale === "zh";
  function set(key: keyof ProgramFilterState, value: string) {
    onChange({ ...filters, [key]: value });
  }
  return (
    <div className="grid gap-3 rounded-2xl border border-line bg-white p-4 shadow-soft md:grid-cols-6">
      <div className="flex items-center gap-2 font-semibold"><SlidersHorizontal size={18} />{zh ? "筛选" : "Filters"}</div>
      <input value={filters.search} onChange={(event) => set("search", event.target.value)} className="rounded-xl border border-line px-3 py-2 text-sm outline-none focus:border-brand" placeholder={zh ? "搜索" : "Search"} />
      <input value={filters.country} onChange={(event) => set("country", event.target.value)} className="rounded-xl border border-line px-3 py-2 text-sm outline-none focus:border-brand" placeholder={zh ? "国家/地区" : "Country"} />
      <input value={filters.field} onChange={(event) => set("field", event.target.value)} className="rounded-xl border border-line px-3 py-2 text-sm outline-none focus:border-brand" placeholder={zh ? "方向" : "Field"} />
      <input value={filters.university} onChange={(event) => set("university", event.target.value)} className="rounded-xl border border-line px-3 py-2 text-sm outline-none focus:border-brand" placeholder={zh ? "学校" : "University"} />
      <select value={filters.review_status} onChange={(event) => set("review_status", event.target.value)} className="rounded-xl border border-line px-3 py-2 text-sm">
        <option value="">{zh ? "审核状态" : "Review status"}</option>
        <option value="auto_extracted">auto_extracted</option>
        <option value="needs_review">needs_review</option>
        <option value="reviewed">reviewed</option>
      </select>
      <select value={filters.min_confidence} onChange={(event) => set("min_confidence", event.target.value)} className="rounded-xl border border-line px-3 py-2 text-sm md:col-start-6">
        <option value="">{zh ? "置信度" : "Confidence"}</option>
        <option value="0.75">75%+</option>
        <option value="0.5">50%+</option>
      </select>
    </div>
  );
}
