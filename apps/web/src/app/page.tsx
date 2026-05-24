"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { fetchAlerts, fetchDailyBriefing, fetchIntelFiles } from "@/lib/api";
import type { AlertSummary } from "@/types/alerts";
import type { BriefingItem } from "@/types/briefings";
import type { IntelFileSummary } from "@/types/intel-files";

type DashboardState =
  | { status: "loading" }
  | {
      status: "ready";
      intelFiles: IntelFileSummary[];
      intelTotal: number;
      alerts: AlertSummary[];
      briefingItems: BriefingItem[];
      overview: string;
    }
  | { status: "error"; message: string };

const statusLabels: Record<string, string> = {
  new: "New",
  watching: "Watching",
  spreading: "Spreading",
  validating: "Validating",
  cooling: "Cooling",
  dormant: "Dormant",
  resurrected: "Resurrected",
  verified: "Verified",
  debunked: "Debunked",
  noise: "Noise",
  archived: "Archived",
};

function formatScore(value: number | null) {
  return value === null ? "-" : value.toFixed(1);
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function topBriefingItems(items: BriefingItem[]) {
  return items.slice(0, 4);
}

export default function HomePage() {
  const [state, setState] = useState<DashboardState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      try {
        const [filesResponse, alertsResponse, briefingResponse] = await Promise.all([
          fetchIntelFiles(1, 8),
          fetchAlerts("pending"),
          fetchDailyBriefing(24),
        ]);

        if (cancelled) {
          return;
        }

        if (!filesResponse.success || !filesResponse.data) {
          setState({ status: "error", message: filesResponse.error?.message ?? "Intel files failed to load." });
          return;
        }
        if (!alertsResponse.success || !alertsResponse.data) {
          setState({ status: "error", message: alertsResponse.error?.message ?? "Alerts failed to load." });
          return;
        }
        if (!briefingResponse.success || !briefingResponse.data) {
          setState({ status: "error", message: briefingResponse.error?.message ?? "Briefing failed to load." });
          return;
        }

        const sections = briefingResponse.data.sections;
        const briefingItems = [
          ...sections.resurrected,
          ...sections.high_opportunity,
          ...sections.updated_files,
          ...sections.new_files,
        ];

        setState({
          status: "ready",
          intelFiles: filesResponse.data.items,
          intelTotal: filesResponse.data.total,
          alerts: alertsResponse.data.items,
          briefingItems,
          overview: briefingResponse.data.overview,
        });
      } catch (error) {
        if (!cancelled) {
          setState({
            status: "error",
            message: error instanceof Error ? error.message : "Dashboard failed to load.",
          });
        }
      }
    }

    void loadDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  const statusCounts = useMemo(() => {
    if (state.status !== "ready") {
      return [];
    }
    const counts = new Map<string, number>();
    for (const item of state.intelFiles) {
      counts.set(item.status, (counts.get(item.status) ?? 0) + 1);
    }
    return Array.from(counts.entries()).map(([status, count]) => ({ status, count }));
  }, [state]);

  if (state.status === "loading") {
    return <div className="text-sm text-slate-400">Loading dashboard...</div>;
  }

  if (state.status === "error") {
    return (
      <section className="max-w-3xl">
        <h1 className="text-2xl font-semibold">Signal Tracker</h1>
        <div className="mt-5 rounded border border-red-900 bg-red-950/40 p-4 text-sm text-red-100">
          {state.message}
        </div>
      </section>
    );
  }

  const topFiles = state.intelFiles.slice(0, 5);
  const openAlerts = state.alerts.slice(0, 4);
  const briefingItems = topBriefingItems(state.briefingItems);

  return (
    <section className="space-y-7">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-medium text-cyan-300">Intelligence lifecycle workbench</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">Signal Tracker</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">{state.overview}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link href="/inbox" className="rounded border border-cyan-500 bg-cyan-500 px-3 py-2 text-sm font-medium text-slate-950">
            Capture Signal
          </Link>
          <Link href="/sources" className="rounded border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:bg-slate-900">
            Run Source Checks
          </Link>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-4">
        <Metric label="Intel files" value={String(state.intelTotal)} />
        <Metric label="Pending alerts" value={String(state.alerts.length)} />
        <Metric label="High opportunity" value={String(state.intelFiles.filter((item) => (item.opportunity_score ?? 0) >= 7).length)} />
        <Metric label="Resurrected" value={String(state.intelFiles.filter((item) => item.status === "resurrected").length)} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
        <section>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Active Intel Files</h2>
            <Link href="/intel-files" className="text-sm text-cyan-300 hover:text-cyan-200">
              View all
            </Link>
          </div>
          <div className="overflow-hidden rounded border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-900 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-4 py-3">Signal</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Opportunity</th>
                  <th className="px-4 py-3">Evidence</th>
                  <th className="px-4 py-3">Last seen</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {topFiles.map((item) => (
                  <tr key={item.id} className="bg-slate-950/60 hover:bg-slate-900/70">
                    <td className="px-4 py-3">
                      <Link href={`/intel-files/${item.id}`} className="font-medium text-slate-100 hover:text-cyan-200">
                        {item.title}
                      </Link>
                      <div className="mt-1 max-w-xl truncate text-xs text-slate-500">{item.thesis ?? "No thesis recorded"}</div>
                    </td>
                    <td className="px-4 py-3 text-slate-300">{statusLabels[item.status] ?? item.status}</td>
                    <td className="px-4 py-3 text-slate-300">{formatScore(item.opportunity_score)}</td>
                    <td className="px-4 py-3 text-slate-300">{item.evidence_count}</td>
                    <td className="px-4 py-3 text-slate-400">{formatDate(item.last_seen_at)}</td>
                  </tr>
                ))}
                {topFiles.length === 0 ? (
                  <tr>
                    <td className="px-4 py-8 text-center text-slate-500" colSpan={5}>
                      No intel files yet.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>

        <aside className="space-y-6">
          <Panel title="Lifecycle Mix">
            <div className="space-y-2">
              {statusCounts.length > 0 ? (
                statusCounts.map((item) => (
                  <div key={item.status} className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">{statusLabels[item.status] ?? item.status}</span>
                    <span className="font-medium text-slate-100">{item.count}</span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">No lifecycle data yet.</p>
              )}
            </div>
          </Panel>

          <Panel title="Pending Alerts">
            <div className="space-y-3">
              {openAlerts.length > 0 ? (
                openAlerts.map((alert) => (
                  <div key={alert.id} className="border-l border-amber-500 pl-3">
                    <div className="text-sm font-medium text-slate-100">{alert.intel_file_title}</div>
                    <div className="mt-1 text-xs leading-5 text-slate-400">{alert.message}</div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">No pending alerts.</p>
              )}
            </div>
          </Panel>

          <Panel title="Briefing Watchlist">
            <div className="space-y-3">
              {briefingItems.length > 0 ? (
                briefingItems.map((item) => (
                  <Link key={item.intel_file_id} href={`/intel-files/${item.intel_file_id}`} className="block rounded border border-slate-800 p-3 hover:bg-slate-900">
                    <div className="text-sm font-medium text-slate-100">{item.title}</div>
                    <div className="mt-1 text-xs text-slate-500">{item.reason}</div>
                  </Link>
                ))
              ) : (
                <p className="text-sm text-slate-500">No briefing items in the last 24 hours.</p>
              )}
            </div>
          </Panel>
        </aside>
      </div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-slate-800 bg-slate-900/60 p-4">
      <div className="text-xs uppercase text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded border border-slate-800 bg-slate-900/40 p-4">
      <h2 className="mb-3 text-sm font-semibold uppercase text-slate-400">{title}</h2>
      {children}
    </section>
  );
}
