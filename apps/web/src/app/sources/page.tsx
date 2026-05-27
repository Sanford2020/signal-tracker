"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  acceptMatchSuggestion,
  fetchSourceProviderHealth,
  fetchSourceCheckRuns,
  generateSourceCheckMatchSuggestions,
  runSourceChecks,
  updateMatchSuggestionStatus,
} from "@/lib/api";
import type { MatchSuggestion } from "@/types/intel-files";
import type { SourceCheckResult, SourceCheckRun, SourceProviderHealth } from "@/types/source-checks";

type PageState =
  | { status: "loading" }
  | {
      status: "ready";
      runs: SourceCheckRun[];
      providerHealth: SourceProviderHealth[];
      latestResults: SourceCheckResult[];
      latestSuggestions: MatchSuggestion[];
      message: string | null;
    }
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
  const [generatingRunId, setGeneratingRunId] = useState<string | null>(null);
  const [actingSuggestionId, setActingSuggestionId] = useState<string | null>(null);

  async function loadRuns(message: string | null = null) {
    try {
      const [runsResponse, healthResponse] = await Promise.all([
        fetchSourceCheckRuns(10),
        fetchSourceProviderHealth(25),
      ]);
      if (!runsResponse.success || !runsResponse.data) {
        setState({ status: "error", message: runsResponse.error?.message ?? "Source check runs failed to load." });
        return;
      }
      if (!healthResponse.success || !healthResponse.data) {
        setState({ status: "error", message: healthResponse.error?.message ?? "Provider health failed to load." });
        return;
      }
      setState({
        status: "ready",
        runs: runsResponse.data.items,
        providerHealth: healthResponse.data.items,
        latestResults: [],
        latestSuggestions: [],
        message,
      });
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
      const suggestionsResponse = await generateSourceCheckMatchSuggestions(response.data.run.id);
      const suggestions =
        suggestionsResponse.success && suggestionsResponse.data ? suggestionsResponse.data.items : [];
      const [runsResponse, healthResponse] = await Promise.all([
        fetchSourceCheckRuns(10),
        fetchSourceProviderHealth(25),
      ]);
      const runs = runsResponse.success && runsResponse.data ? runsResponse.data.items : [response.data.run];
      const providerHealth = healthResponse.success && healthResponse.data ? healthResponse.data.items : [];
      setState({
        status: "ready",
        runs,
        providerHealth,
        latestResults: response.data.results,
        latestSuggestions: suggestions,
        message: `Run ${response.data.run.status}: checked ${response.data.run.checked_query_count} queries, found ${response.data.run.result_count} results, and created ${suggestions.length} suggestions.`,
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

  async function handleGenerateSuggestions(run: SourceCheckRun) {
    setGeneratingRunId(run.id);
    try {
      const response = await generateSourceCheckMatchSuggestions(run.id);
      if (!response.success || !response.data) {
        setState({ status: "error", message: response.error?.message ?? "Suggestion generation failed." });
        return;
      }
      const data = response.data;
      setState((current) => {
        if (current.status !== "ready") {
          return current;
        }
        return {
          ...current,
          latestSuggestions: data.items,
          message: `Created ${data.created_count} suggestions from ${formatDate(run.started_at)} run.`,
        };
      });
    } catch (error) {
      setState({
        status: "error",
        message: error instanceof Error ? error.message : "Suggestion generation failed.",
      });
    } finally {
      setGeneratingRunId(null);
    }
  }

  function replaceSuggestion(updated: MatchSuggestion, message: string) {
    setState((current) => {
      if (current.status !== "ready") {
        return current;
      }
      return {
        ...current,
        latestSuggestions: current.latestSuggestions.map((item) =>
          item.id === updated.id ? updated : item,
        ),
        message,
      };
    });
  }

  async function handleAcceptSuggestion(suggestion: MatchSuggestion) {
    setActingSuggestionId(suggestion.id);
    try {
      const response = await acceptMatchSuggestion(suggestion.id, suggestion.rationale);
      if (!response.success || !response.data) {
        setState({ status: "error", message: response.error?.message ?? "Suggestion accept failed." });
        return;
      }
      replaceSuggestion(
        response.data.item,
        `Accepted suggestion and attached evidence to intel file ${suggestion.intel_file_id}.`,
      );
    } catch (error) {
      setState({
        status: "error",
        message: error instanceof Error ? error.message : "Suggestion accept failed.",
      });
    } finally {
      setActingSuggestionId(null);
    }
  }

  async function handleDismissSuggestion(suggestion: MatchSuggestion) {
    setActingSuggestionId(suggestion.id);
    try {
      const response = await updateMatchSuggestionStatus(suggestion.id, "dismissed");
      if (!response.success || !response.data) {
        setState({ status: "error", message: response.error?.message ?? "Suggestion dismiss failed." });
        return;
      }
      replaceSuggestion(response.data.item, `Dismissed suggestion for ${suggestion.result_title}.`);
    } catch (error) {
      setState({
        status: "error",
        message: error instanceof Error ? error.message : "Suggestion dismiss failed.",
      });
    } finally {
      setActingSuggestionId(null);
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
        <Metric label="Provider hints" value={String(state.providerHealth.length)} />
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
                  <th className="px-4 py-3">Actions</th>
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
                    <td className="px-4 py-3">
                      <button
                        type="button"
                        onClick={() => void handleGenerateSuggestions(run)}
                        disabled={generatingRunId === run.id || run.result_count === 0}
                        className="text-xs font-medium text-cyan-300 disabled:cursor-not-allowed disabled:text-slate-600"
                      >
                        {generatingRunId === run.id ? "Generating..." : "Suggest"}
                      </button>
                    </td>
                  </tr>
                ))}
                {state.runs.length === 0 ? (
                  <tr>
                    <td className="px-4 py-8 text-center text-slate-500" colSpan={6}>
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

      <section>
        <h2 className="mb-3 text-lg font-semibold">Provider Health</h2>
        <div className="overflow-hidden rounded border border-slate-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Hint</th>
                <th className="px-4 py-3">Enabled queries</th>
                <th className="px-4 py-3">Recent results</th>
                <th className="px-4 py-3">Recent errors</th>
                <th className="px-4 py-3">Last result</th>
                <th className="px-4 py-3">Latest run</th>
                <th className="px-4 py-3">Provider error</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {state.providerHealth.map((item) => (
                <tr key={item.source_hint} className="bg-slate-950/60">
                  <td className="px-4 py-3 font-medium text-slate-100">{item.source_hint}</td>
                  <td className="px-4 py-3 text-slate-300">{item.enabled_query_count}</td>
                  <td className="px-4 py-3 text-slate-300">{item.recent_result_count}</td>
                  <td className={item.recent_error_count > 0 ? "px-4 py-3 text-amber-300" : "px-4 py-3 text-slate-300"}>
                    {item.recent_error_count}
                  </td>
                  <td className="px-4 py-3 text-slate-300">{formatDate(item.last_result_at)}</td>
                  <td className="px-4 py-3 text-slate-300">{item.latest_run_status ?? "-"}</td>
                  <td className="max-w-sm truncate px-4 py-3 text-slate-500">{item.latest_error ?? "-"}</td>
                </tr>
              ))}
              {state.providerHealth.length === 0 ? (
                <tr>
                  <td className="px-4 py-8 text-center text-slate-500" colSpan={7}>
                    Generate tracking queries and run source checks to populate provider health.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Suggested Evidence</h2>
        <div className="grid gap-3 lg:grid-cols-2">
          {state.latestSuggestions.length > 0 ? (
            state.latestSuggestions.map((suggestion) => (
              <div
                key={suggestion.id}
                className="rounded border border-slate-800 bg-slate-900/40 p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <Link
                      href={`/intel-files/${suggestion.intel_file_id}`}
                      className="block truncate text-sm font-medium text-slate-100 hover:text-cyan-200"
                    >
                      {suggestion.result_title}
                    </Link>
                    <p className="mt-1 text-xs text-cyan-300">{suggestion.source_name ?? "source"} · {(suggestion.confidence * 100).toFixed(0)}%</p>
                  </div>
                  <span className="shrink-0 rounded border border-slate-700 px-2 py-1 text-xs text-slate-400">
                    {suggestion.status}
                  </span>
                </div>
                <p className="mt-2 line-clamp-2 text-xs leading-5 text-slate-400">{suggestion.rationale}</p>
                <div className="mt-4 flex flex-wrap items-center gap-3">
                  {suggestion.result_url ? (
                    <a
                      href={suggestion.result_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs font-medium text-slate-400 hover:text-cyan-200"
                    >
                      Open source
                    </a>
                  ) : null}
                  <button
                    type="button"
                    onClick={() => void handleAcceptSuggestion(suggestion)}
                    disabled={suggestion.status !== "open" || actingSuggestionId === suggestion.id}
                    className="rounded border border-emerald-500 bg-emerald-500 px-2.5 py-1.5 text-xs font-medium text-slate-950 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {actingSuggestionId === suggestion.id ? "Working..." : "Accept"}
                  </button>
                  <button
                    type="button"
                    onClick={() => void handleDismissSuggestion(suggestion)}
                    disabled={suggestion.status !== "open" || actingSuggestionId === suggestion.id}
                    className="rounded border border-slate-700 px-2.5 py-1.5 text-xs font-medium text-slate-300 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="rounded border border-slate-800 bg-slate-900/40 p-4 text-sm text-slate-500">
              Generate suggestions from a run with results to create candidate follow-up evidence.
            </div>
          )}
        </div>
      </section>
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
