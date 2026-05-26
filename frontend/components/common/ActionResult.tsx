export function ActionResult({ title, message, data, error, locale }: { title?: string; message?: string | null; data: unknown; error?: string | null; locale: string }) {
  if (!data && !error) return null;

  if (error) {
    return (
      <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        <div className="mb-1 font-semibold">{locale === "zh" ? "请求失败" : "Request Failed"}</div>
        <pre className="max-h-48 overflow-auto whitespace-pre-wrap text-xs">{error}</pre>
      </div>
    );
  }

  return (
    <div className="mt-4 rounded-2xl border border-green-200 bg-green-50 p-4 text-sm">
      {message && <p className="font-medium text-green-800">{message}</p>}
      <details className="mt-2">
        <summary className="cursor-pointer text-xs text-muted hover:text-gray-700">
          {locale === "zh" ? "查看原始数据" : "View raw data"}
        </summary>
        <pre className="mt-2 max-h-60 overflow-auto rounded-xl bg-gray-950 p-3 text-xs text-gray-100 whitespace-pre-wrap">
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  );
}
