"use client";

import { useEffect, useState } from "react";
import { Search } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

type UniversityBrief = {
  id: number;
  name: string;
  short_name: string | null;
  country: string;
  city: string | null;
};

export function RegionUniversitySelector({
  locale,
  onUniversityChange,
}: {
  locale: string;
  onUniversityChange: (id: number | null) => void;
}) {
  const zh = locale === "zh";
  const [regions, setRegions] = useState<string[]>([]);
  const [selectedRegion, setSelectedRegion] = useState("");
  const [universities, setUniversities] = useState<UniversityBrief[]>([]);
  const [selectedUniversityId, setSelectedUniversityId] = useState<number | null>(null);
  const [loadingRegions, setLoadingRegions] = useState(true);
  const [loadingUniversities, setLoadingUniversities] = useState(false);

  useEffect(() => {
    fetch(`${API}/discovery/regions`)
      .then((r) => r.json())
      .then((data) => setRegions(data))
      .catch(() => {})
      .finally(() => setLoadingRegions(false));
  }, []);

  useEffect(() => {
    if (!selectedRegion) {
      setUniversities([]);
      setSelectedUniversityId(null);
      onUniversityChange(null);
      return;
    }
    setLoadingUniversities(true);
    fetch(`${API}/discovery/universities?region=${encodeURIComponent(selectedRegion)}`)
      .then((r) => r.json())
      .then((data) => setUniversities(data))
      .catch(() => {})
      .finally(() => setLoadingUniversities(false));
  }, [selectedRegion]);

  function handleUniversityChange(id: number | null) {
    setSelectedUniversityId(id);
    onUniversityChange(id);
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="mb-1.5 block text-sm font-semibold text-ink">
          {zh ? "地区" : "Region"}
        </label>
        <select
          value={selectedRegion}
          onChange={(e) => setSelectedRegion(e.target.value)}
          className="w-full rounded-xl border border-line bg-white px-3 py-2.5 text-sm"
          disabled={loadingRegions}
        >
          <option value="">
            {loadingRegions
              ? zh ? "加载中..." : "Loading..."
              : zh ? "选择地区" : "Select region"}
          </option>
          {regions.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="mb-1.5 block text-sm font-semibold text-ink">
          {zh ? "学校" : "University"}
        </label>
        <select
          value={selectedUniversityId ?? ""}
          onChange={(e) => handleUniversityChange(e.target.value ? Number(e.target.value) : null)}
          className="w-full rounded-xl border border-line bg-white px-3 py-2.5 text-sm"
          disabled={!selectedRegion || loadingUniversities}
        >
          <option value="">
            {loadingUniversities
              ? zh ? "加载中..." : "Loading..."
              : zh ? "选择学校" : "Select university"}
          </option>
          {universities.map((u) => (
            <option key={u.id} value={u.id}>
              {u.short_name ? `${u.short_name} - ${u.name}` : u.name}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
