"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { fetchIntelFiles } from "@/lib/api";
import type { IntelFileSummary } from "@/types/intel-files";

function formatScore(value: number | null) {
  return value === null ? "—" : value.toFixed(1);
}

export default function IntelFilesPage() {
  const [items, setItems] = useState<IntelFileSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadFiles = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchIntelFiles();
      if (!result.success || !result.data) {
        setError(result.error?.message ?? "Failed to load intel files.");
        setItems([]);
        return;
      }
      setItems(result.data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load intel files.");
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadFiles();
  }, [loadFiles]);

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Intel Files</h1>
          <p className="mt-2 text-slate-400">Tracked intelligence cases promoted from analyzed signals.</p>
        </div>
        <button
          type="button"
          onClick={() => void loadFiles()}
          className="text-sm text-sky-400 hover:text-sky-300"
        >
          Refresh
        </button>
      </div>

      {loading ? <p className="text-sm text-slate-400">Loading intel files...</p> : null}
      {error ? <p className="text-sm text-red-400">{error}</p> : null}

      {!loading && !error && items.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-800 p-6 text-sm text-slate-400">
          No intel files yet. Analyze an inbox item and create your first file.
        </div>
      ) : null}

      {!loading && !error && items.length > 0 ? (
        <div className="overflow-hidden rounded-lg border border-slate-800">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-900 text-left text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">Title</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">First seen</th>
                <th className="px-4 py-3 font-medium">Evidence</th>
                <th className="px-4 py-3 font-medium">Heat</th>
                <th className="px-4 py-3 font-medium">Opportunity</th>
                <th className="px-4 py-3 font-medium">Risk</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-t border-slate-800">
                  <td className="px-4 py-3">
                    <Link href={`/intel-files/${item.id}`} className="text-sky-300 hover:text-sky-200">
                      {item.title}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded bg-slate-800 px-2 py-1 text-xs uppercase text-slate-300">
                      {item.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-400">
                    {new Date(item.first_seen_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3">{item.evidence_count}</td>
                  <td className="px-4 py-3">{formatScore(item.heat_score)}</td>
                  <td className="px-4 py-3">{formatScore(item.opportunity_score)}</td>
                  <td className="px-4 py-3">{formatScore(item.risk_score)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}
