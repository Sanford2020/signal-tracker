"use client";

import { useEffect, useState } from "react";

import { fetchSourceCheckRuns, runSourceChecks } from "@/lib/api";
import type { SourceCheckResult, SourceCheckRun } from "@/types/source-checks";

type PageState =
  | { status: "loading" }
  | { status: "ready"; runs: SourceCheckRun[]; latestResults: SourceCheckResult[]; message: string | null }
  | { status: "error"; message: string };

function formatDate(value: string | null) {
  if (!value) {
    return "-";
  }
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export default function SourcesPage() {
  const [state, setState] = useState<PageState>({ status: "loading" });
  const [isRunning, setIsRunning] = useState(false);

  async function loadRuns(message: string | null = null) {
    try {
      const response = await fetchSourceCheckRuns(10);
      if (!response.success || !response.data) {
        setState({ status: "error", message: response.error?.message ?? "Source check runs failed to load." });
        return;
      }
      setState({ status: "ready", runs: response.data.items, latestResults: [], message });
    } catch (error) {
      setState({
        status: "error",
        message: error instanceof Error ? error.message : "Source check runs failed to load.",
      });
    }
  }

  useEffect(() => {
    void loadRuns();
  }, []);

  async function handleRunChecks() {
    setIsRunning(true);
    try {
      const response = await runSourceChecks(20);
      if (!response.success || !response.data) {
        setState({ status: "error", message: response.error?.message ?? "Source check failed." });
        return;
      }
      const runsResponse = await fetchSourceCheckRuns(10);
      const runs = runsResponse.success && runsResponse.data ? runsResponse.data.items : [response.data.run];
      setState({
        status: "ready",
        runs,
        latestResults: response.data.results,
        message: `Run ${response.data.run.status}: checked ${response.data.run.checked_query_count} queries and found ${response.data.run.result_count} results.`,
      });
    } catch (error) {
      setState({
        status: "error",
        message: error instanceof Error ? error.message : "Source check failed.",
      });
    } finally {
      setIsRunning(false);
    }
  }

  if (state.status === "loading") {
    return <div className="text-sm text-slate-400">Loading source operations...</div>;
  }

  if (state.status === "error") {
    return (
      <section className="max-w-3xl">
        <h1 className="text-2xl font-semibold">Sources</h1>
        <div className="mt-5 rounded border border-red-900 bg-red-950/40 p-4 text-sm text-red-100">
          {state.message}
        </div>
      </section>
    );
  }

  return (
    <section className="space-y-7">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-medium text-cyan-300">Provider operations</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">Sources</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
            Run configured providers, inspect recent source-check jobs, and review newly discovered follow-up evidence.
          </p>
        </div>
        <button
          type="button"
          onClick={handleRunChecks}
          disabled={isRunning}
          className="rounded border border-cyan-500 bg-cyan-500 px-3 py-2 text-sm font-medium text-slate-950 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isRunning ? "Running..." : "Run Source Checks"}
        </button>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        <Metric label="Recent runs" value={String(state.runs.length)} />
        <Metric label="Last checked queries" value={String(state.runs[0]?.checked_query_count ?? 0)} />
        <Metric label="Last result count" value={String(state.runs[0]?.result_count ?? 0)} />
      </div>

      {state.message ? (
        <div className="rounded border border-cyan-900 bg-cyan-950/30 p-4 text-sm text-cyan-100">
          {state.message}
        </div>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
        <section>
          <h2 className="mb-3 text-lg font-semibold">Run History</h2>
          <div className="overflow-hidden rounded border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-900 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-4 py-3">Started</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Queries</th>
                  <th className="px-4 py-3">Results</th>
                  <th className="px-4 py-3">Error</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {state.runs.map((run) => (
                  <tr key={run.id} className="bg-slate-950/60">
                    <td className="px-4 py-3 text-slate-300">{formatDate(run.started_at)}</td>
                    <td className="px-4 py-3 text-slate-300">{run.status}</td>
                    <td className="px-4 py-3 text-slate-300">{run.checked_query_count}</td>
                    <td className="px-4 py-3 text-slate-300">{run.result_count}</td>
                    <td className="max-w-xs truncate px-4 py-3 text-slate-500">{run.error ?? "-"}</td>
                  </tr>
                ))}
                {state.runs.length === 0 ? (
                  <tr>
                    <td className="px-4 py-8 text-center text-slate-500" colSpan={5}>
                      No source check runs yet.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>

        <aside>
          <h2 className="mb-3 text-lg font-semibold">Latest Results</h2>
          <div className="space-y-3">
            {state.latestResults.length > 0 ? (
              state.latestResults.map((result) => (
                <a
                  key={result.id}
                  href={result.url ?? "#"}
                  target={result.url ? "_blank" : undefined}
                  rel="noreferrer"
                  className="block rounded border border-slate-800 bg-slate-900/40 p-4 hover:bg-slate-900"
                >
                  <div className="text-sm font-medium text-slate-100">{result.title}</div>
                  <div className="mt-1 text-xs text-cyan-300">{result.source_name ?? result.source_hint ?? "source"}</div>
                  {result.snippet ? <p className="mt-2 line-clamp-3 text-xs leading-5 text-slate-400">{result.snippet}</p> : null}
                </a>
              ))
            ) : (
              <div className="rounded border border-slate-800 bg-slate-900/40 p-4 text-sm text-slate-500">
                Run source checks to inspect the latest provider results.
              </div>
            )}
          </div>
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
