"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { fetchAlerts, updateAlertStatus } from "@/lib/api";
import type { AlertSummary } from "@/types/alerts";

export default function AlertsPage() {
  const [items, setItems] = useState<AlertSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const loadAlerts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchAlerts();
      if (!result.success || !result.data) {
        setError(result.error?.message ?? "Failed to load alerts.");
        setItems([]);
        return;
      }
      setItems(result.data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load alerts.");
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadAlerts();
  }, [loadAlerts]);

  async function handleUpdate(alertId: string, status: "acknowledged" | "dismissed") {
    setUpdatingId(alertId);
    setError(null);
    try {
      const result = await updateAlertStatus(alertId, { status });
      if (!result.success) {
        setError(result.error?.message ?? "Failed to update alert.");
        return;
      }
      await loadAlerts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update alert.");
    } finally {
      setUpdatingId(null);
    }
  }

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Alerts</h1>
          <p className="mt-2 text-slate-400">
            Lifecycle and score-threshold notifications for tracked intel files.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void loadAlerts()}
          className="text-sm text-sky-400 hover:text-sky-300"
        >
          Refresh
        </button>
      </div>

      {loading ? <p className="text-sm text-slate-400">Loading alerts...</p> : null}
      {error ? <p className="text-sm text-red-400">{error}</p> : null}

      {!loading && !error && items.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-800 p-6 text-sm text-slate-400">
          No alerts yet. Evaluate lifecycle or rescore files to generate notifications.
        </div>
      ) : null}

      {!loading && !error && items.length > 0 ? (
        <div className="overflow-hidden rounded-lg border border-slate-800">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-900 text-left text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">Severity</th>
                <th className="px-4 py-3 font-medium">Type</th>
                <th className="px-4 py-3 font-medium">File</th>
                <th className="px-4 py-3 font-medium">Message</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Created</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-t border-slate-800">
                  <td className="px-4 py-3 uppercase text-xs">{item.severity}</td>
                  <td className="px-4 py-3 text-slate-300">{item.alert_type}</td>
                  <td className="px-4 py-3">
                    <Link
                      href={`/intel-files/${item.intel_file_id}`}
                      className="text-sky-300 hover:text-sky-200"
                    >
                      {item.intel_file_title}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-slate-400">{item.message}</td>
                  <td className="px-4 py-3">{item.status}</td>
                  <td className="px-4 py-3 text-slate-400">
                    {new Date(item.created_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 space-x-2">
                    {item.status === "pending" || item.status === "sent" ? (
                      <>
                        <button
                          type="button"
                          disabled={updatingId === item.id}
                          onClick={() => void handleUpdate(item.id, "acknowledged")}
                          className="rounded border border-slate-700 px-2 py-1 text-xs text-emerald-300 hover:bg-slate-800 disabled:opacity-50"
                        >
                          Acknowledge
                        </button>
                        <button
                          type="button"
                          disabled={updatingId === item.id}
                          onClick={() => void handleUpdate(item.id, "dismissed")}
                          className="rounded border border-slate-700 px-2 py-1 text-xs text-slate-300 hover:bg-slate-800 disabled:opacity-50"
                        >
                          Dismiss
                        </button>
                      </>
                    ) : (
                      <span className="text-xs text-slate-500">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}
