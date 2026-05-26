export function EmptyState({ title, body }: { title: string; body: string }) {
  return <div className="rounded-2xl border border-dashed border-line bg-white p-10 text-center"><h3 className="font-semibold">{title}</h3><p className="mt-2 text-sm text-muted">{body}</p></div>;
}
