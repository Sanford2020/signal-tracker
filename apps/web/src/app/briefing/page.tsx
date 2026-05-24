"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { fetchDailyBriefing, fetchWeeklyRetrospective } from "@/lib/api";
import type { BriefingItem, DailyBriefingData, WeeklyRetrospectiveData } from "@/types/briefings";

const SECTION_LABELS: Array<[keyof DailyBriefingData["sections"], string]> = [
  ["resurrected", "Resurrected Signals"],
  ["high_opportunity", "High Opportunity"],
  ["risk_or_noise", "Risk / Noise"],
  ["new_files", "New Intel Files"],
  ["updated_files", "Updated Intel Files"],
];

const WEEKLY_SECTION_LABELS: Array<[keyof WeeklyRetrospectiveData["sections"], string]> = [
  ["changed_files", "Changed Files"],
  ["resurrected", "Resurrected Signals"],
  ["verified_or_debunked", "Verified / Debunked"],
  ["opportunity_gainers", "Opportunity Gainers"],
  ["cooling_or_noise", "Cooling / Noise"],
];

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function formatScore(value: number | null) {
  return value === null ? "-" : value.toFixed(1);
}

function BriefingCard({ item }: { item: BriefingItem }) {
  return (
    <li className="rounded-lg border border-slate-800 p-4">
      <div className="flex flex-wrap items-center gap-3">
        <Link href={`/intel-files/${item.intel_file_id}`} className="font-medium text-sky-300 hover:text-sky-200">
          {item.title}
        </Link>
        <span className="rounded bg-slate-800 px-2 py-1 text-xs uppercase text-slate-300">{item.status}</span>
      </div>
      <p className="mt-2 text-sm text-slate-400">{item.reason}</p>
      <div className="mt-3 grid gap-2 text-xs text-slate-300 sm:grid-cols-4">
        <span>Heat {formatScore(item.scores.heat)}</span>
        <span>Cred {formatScore(item.scores.credibility)}</span>
        <span>Opp {formatScore(item.scores.opportunity)}</span>
        <span>Risk {formatScore(item.scores.risk)}</span>
      </div>
      {item.key_evidence.length > 0 ? (
        <div className="mt-3 space-y-1 text-xs text-slate-500">
          {item.key_evidence.map((evidence) => (
            <p key={evidence.raw_item_id}>
              Evidence:{" "}
              {evidence.url ? (
                <a href={evidence.url} target="_blank" rel="noreferrer" className="text-sky-400 hover:text-sky-300">
                  {evidence.title}
                </a>
              ) : (
                evidence.title
              )}
            </p>
          ))}
        </div>
      ) : null}
    </li>
  );
}

export default function BriefingPage() {
  const [briefing, setBriefing] = useState<DailyBriefingData | null>(null);
  const [weekly, setWeekly] = useState<WeeklyRetrospectiveData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<"daily" | "weekly">("daily");
  const [hours, setHours] = useState(24);
  const [days, setDays] = useState(7);

  const loadBriefing = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = mode === "daily" ? await fetchDailyBriefing(hours) : await fetchWeeklyRetrospective(days);
      if (!result.success || !result.data) {
        setError(result.error?.message ?? "Failed to load briefing.");
        setBriefing(null);
        setWeekly(null);
        return;
      }
      if (mode === "daily") {
        setBriefing(result.data as DailyBriefingData);
        setWeekly(null);
      } else {
        setWeekly(result.data as WeeklyRetrospectiveData);
        setBriefing(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load briefing.");
      setBriefing(null);
      setWeekly(null);
    } finally {
      setLoading(false);
    }
  }, [days, hours, mode]);

  const markdownHref =
    mode === "daily"
      ? `${API_BASE}/api/v1/reports/daily.md?hours=${hours}`
      : `${API_BASE}/api/v1/reports/weekly.md?days=${days}`;
  const pdfHref =
    mode === "daily"
      ? `${API_BASE}/api/v1/reports/daily.pdf?hours=${hours}`
      : `${API_BASE}/api/v1/reports/weekly.pdf?days=${days}`;

  useEffect(() => {
    void loadBriefing();
  }, [loadBriefing]);

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold">Briefing</h1>
          <p className="mt-2 text-slate-400">Operating summary and retrospective review of meaningful file changes.</p>
        </div>
        <div className="flex items-center gap-3">
          <select value={mode} onChange={(event) => setMode(event.target.value as "daily" | "weekly")} className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm">
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
          </select>
          {mode === "daily" ? (
            <select
              value={hours}
              onChange={(event) => setHours(Number(event.target.value))}
              className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            >
              <option value={24}>24h</option>
              <option value={48}>48h</option>
              <option value={72}>72h</option>
              <option value={168}>7d</option>
            </select>
          ) : (
            <select
              value={days}
              onChange={(event) => setDays(Number(event.target.value))}
              className="rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            >
              <option value={7}>7d</option>
              <option value={14}>14d</option>
              <option value={31}>31d</option>
            </select>
          )}
          <button type="button" onClick={() => void loadBriefing()} className="text-sm text-sky-400 hover:text-sky-300">
            Refresh
          </button>
          <a href={markdownHref} className="text-sm text-sky-400 hover:text-sky-300">
            Markdown
          </a>
          <a href={pdfHref} className="text-sm text-sky-400 hover:text-sky-300">
            PDF
          </a>
        </div>
      </div>

      {loading ? <p className="text-sm text-slate-400">Loading briefing...</p> : null}
      {error ? <p className="text-sm text-red-400">{error}</p> : null}

      {!loading && !error && briefing ? (
        <>
          <div className="rounded-lg border border-slate-800 p-4">
            <p className="text-sm text-slate-300">{briefing.overview}</p>
            <p className="mt-2 text-xs text-slate-500">
              Generated {new Date(briefing.meta.generated_at).toLocaleString()}
            </p>
          </div>

          {SECTION_LABELS.map(([key, label]) => {
            const items = briefing.sections[key];
            return (
              <section key={key} className="space-y-3">
                <h2 className="text-lg font-medium">{label}</h2>
                {items.length === 0 ? (
                  <div className="rounded-lg border border-dashed border-slate-800 p-4 text-sm text-slate-500">
                    No items in this section for the selected window.
                  </div>
                ) : (
                  <ul className="space-y-3">
                    {items.map((item) => (
                      <BriefingCard key={`${key}-${item.intel_file_id}`} item={item} />
                    ))}
                  </ul>
                )}
              </section>
            );
          })}
        </>
      ) : null}

      {!loading && !error && weekly ? (
        <>
          <div className="rounded-lg border border-slate-800 p-4">
            <p className="text-sm text-slate-300">{weekly.overview}</p>
            <p className="mt-2 text-xs text-slate-500">
              Generated {new Date(weekly.meta.generated_at).toLocaleString()}
            </p>
          </div>

          {WEEKLY_SECTION_LABELS.map(([key, label]) => {
            const items = weekly.sections[key];
            return (
              <section key={key} className="space-y-3">
                <h2 className="text-lg font-medium">{label}</h2>
                {items.length === 0 ? (
                  <div className="rounded-lg border border-dashed border-slate-800 p-4 text-sm text-slate-500">
                    No items in this section for the selected window.
                  </div>
                ) : (
                  <ul className="space-y-3">
                    {items.map((item) => (
                      <BriefingCard key={`${key}-${item.intel_file_id}`} item={item} />
                    ))}
                  </ul>
                )}
              </section>
            );
          })}
        </>
      ) : null}
    </section>
  );
}
