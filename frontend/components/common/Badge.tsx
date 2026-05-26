export function Badge({ children, tone = "neutral" }: { children: React.ReactNode; tone?: "neutral" | "success" | "warning" | "danger" | "brand" }) {
  const styles = {
    neutral: "bg-gray-50 text-gray-700 border-gray-200",
    success: "bg-emerald-50 text-emerald-700 border-emerald-200",
    warning: "bg-amber-50 text-amber-700 border-amber-200",
    danger: "bg-rose-50 text-rose-700 border-rose-200",
    brand: "bg-indigo-50 text-indigo-700 border-indigo-200"
  };
  return <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${styles[tone]}`}>{children}</span>;
}
