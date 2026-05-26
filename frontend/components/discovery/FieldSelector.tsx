"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export function FieldSelector({
  locale,
  onFieldChange,
}: {
  locale: string;
  onFieldChange: (field: string | null) => void;
}) {
  const zh = locale === "zh";
  const [fields, setFields] = useState<string[]>([]);
  const [selectedField, setSelectedField] = useState("");

  useEffect(() => {
    fetch(`${API}/discovery/fields`)
      .then((r) => r.json())
      .then((data) => setFields(data))
      .catch(() => {});
  }, []);

  function handleChange(value: string) {
    setSelectedField(value);
    onFieldChange(value || null);
  }

  return (
    <div>
      <label className="mb-1.5 block text-sm font-semibold text-ink">
        {zh ? "专业方向" : "Field of Study"}
      </label>
      <select
        value={selectedField}
        onChange={(e) => handleChange(e.target.value)}
        className="w-full rounded-xl border border-line bg-white px-3 py-2.5 text-sm"
      >
        <option value="">{zh ? "不限方向" : "Any field"}</option>
        {fields.map((f) => (
          <option key={f} value={f}>
            {f}
          </option>
        ))}
      </select>
    </div>
  );
}
