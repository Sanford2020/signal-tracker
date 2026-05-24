"use client";

import Link from "next/link";

import type { InboxListItem } from "@/types/inbox";

type Props = {
  items: InboxListItem[];
  loading: boolean;
  error: string | null;
  analyzingId: string | null;
  creatingId: string | null;
  onAnalyze: (rawItemId: string) => void;
  onCreateIntelFile: (rawItemId: string) => void;
};

export function InboxList({
  items,
  loading,
  error,
  analyzingId,
  creatingId,
  onAnalyze,
  onCreateIntelFile,
}: Props) {
  if (loading) {
    return <p className="text-sm text-slate-400">Loading inbox...</p>;
  }

  if (error) {
    return <p className="text-sm text-red-400">{error}</p>;
  }

  if (items.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-slate-800 p-6 text-sm text-slate-400">
        No signals yet. Submit a URL or pasted text to start tracking.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-800">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-900 text-left text-slate-400">
          <tr>
            <th className="px-4 py-3 font-medium">Title</th>
            <th className="px-4 py-3 font-medium">URL</th>
            <th className="px-4 py-3 font-medium">Analysis</th>
            <th className="px-4 py-3 font-medium">Intel file</th>
            <th className="px-4 py-3 font-medium">Captured</th>
            <th className="px-4 py-3 font-medium">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.raw_item.id} className="border-t border-slate-800">
              <td className="px-4 py-3">{item.raw_item.title}</td>
              <td className="px-4 py-3 text-slate-400">
                {item.raw_item.url ? (
                  <a href={item.raw_item.url} className="hover:text-sky-400" target="_blank" rel="noreferrer">
                    {item.raw_item.url}
                  </a>
                ) : (
                  "—"
                )}
              </td>
              <td className="px-4 py-3">
                <span
                  className={
                    item.analysis_status === "pending"
                      ? "rounded bg-amber-950 px-2 py-1 text-xs text-amber-300"
                      : "rounded bg-emerald-950 px-2 py-1 text-xs text-emerald-300"
                  }
                >
                  {item.analysis_status}
                </span>
              </td>
              <td className="px-4 py-3">
                {item.has_intel_file ? (
                  <span className="rounded bg-sky-950 px-2 py-1 text-xs text-sky-300">created</span>
                ) : (
                  <span className="text-xs text-slate-500">—</span>
                )}
              </td>
              <td className="px-4 py-3 text-slate-400">
                {new Date(item.raw_item.captured_at).toLocaleString()}
              </td>
              <td className="px-4 py-3 space-x-2">
                {item.analysis_status === "pending" ? (
                  <button
                    type="button"
                    onClick={() => onAnalyze(item.raw_item.id)}
                    disabled={analyzingId === item.raw_item.id}
                    className="rounded border border-slate-700 px-2 py-1 text-xs text-sky-300 hover:bg-slate-800 disabled:opacity-50"
                  >
                    {analyzingId === item.raw_item.id ? "Analyzing..." : "Analyze"}
                  </button>
                ) : item.has_intel_file ? (
                  <Link
                    href="/intel-files"
                    className="rounded border border-slate-700 px-2 py-1 text-xs text-slate-300 hover:bg-slate-800"
                  >
                    View files
                  </Link>
                ) : (
                  <button
                    type="button"
                    onClick={() => onCreateIntelFile(item.raw_item.id)}
                    disabled={creatingId === item.raw_item.id}
                    className="rounded border border-slate-700 px-2 py-1 text-xs text-emerald-300 hover:bg-slate-800 disabled:opacity-50"
                  >
                    {creatingId === item.raw_item.id ? "Creating..." : "Create Intel File"}
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
