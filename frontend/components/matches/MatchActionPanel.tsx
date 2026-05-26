"use client";

import { useState } from "react";
import { Button } from "../common/Button";
import { Card } from "../common/Card";
import { ActionResult } from "../common/ActionResult";

export function MatchActionPanel({ locale }: { locale: string }) {
  const zh = locale === "zh";
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const generateResponse = await fetch("http://127.0.0.1:8000/api/matches/generate/1", { method: "POST" });
      const generateJson = await generateResponse.json();
      if (!generateResponse.ok) throw new Error(JSON.stringify(generateJson));
      const listResponse = await fetch("http://127.0.0.1:8000/api/matches/1");
      const listJson = await listResponse.json();
      if (!listResponse.ok) throw new Error(JSON.stringify(listJson));
      setResult({ generate: generateJson, matches: listJson });
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="mb-6 p-5">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h3 className="font-semibold">{zh ? "匹配引擎" : "Matching Engine"}</h3>
          <p className="mt-2 text-sm text-muted">{zh ? "基于 demo applicant 和当前项目库生成匹配分数，并返回可检查的 JSON。" : "Generate match scores from the demo applicant and current program database, with inspectable JSON output."}</p>
        </div>
        <Button disabled={loading} onClick={generate}>{loading ? (zh ? "生成中..." : "Generating...") : (zh ? "生成匹配" : "Generate Matches")}</Button>
      </div>
      <ActionResult locale={locale} data={result} error={error} />
    </Card>
  );
}
