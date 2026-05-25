"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { fetchIntelFiles } from "@/lib/api";
import type { IntelFileSummary } from "@/types/intel-files";

const statuses = [
  { value: "", label: "All statuses" },
  { value: "new", label: "New" },
  { value: "watching", label: "Watching" },
  { value: "spreading", label: "Spreading" },
  { value: "validating", label: "Validating" },
  { value: "cooling", label: "Cooling" },
  { value: "dormant", label: "Dormant" },
  { value: "resurrected", label: "Resurrected" },
  { value: "verified", label: "Verified" },
  { value: "debunked", label: "Debunked" },
  { value: "noise", label: "Noise" },
  { value: "archived", label: "Archived" },
];

const sortOptions = [
  { value: "updated_at", label: "Updated" },
  { value: "last_seen_at", label: "Last seen" },
  { value: "first_seen_at", label: "First seen" },
  { value: "opportunity_score", label: "Opportunity" },
  { value: "heat_score", label: "Heat" },
  { value: "risk_score", label: "Risk" },
  { value: "evidence_count", label: "Evidence" },
];

const SAVED_VIEW_KEY = "signal-tracker:intel-file-saved-views";

type SavedViewFilters = {
  query: string;
  status: string;
  sort: string;
  order: "asc" | "desc";
  pageSize: number;
};

type SavedView = SavedViewFilters & {
  id: string;
  name: string;
  createdAt: string;
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

function loadSavedViews(): SavedView[] {
  if (typeof window === "undefined") {
    return [];
  }
  const rawValue = window.localStorage.getItem(SAVED_VIEW_KEY);
  if (!rawValue) {
    return [];
  }
  try {
    const parsed = JSON.parse(rawValue);
    return Array.isArray(parsed) ? parsed.filter(isSavedView) : [];
  } catch {
    return [];
  }
}

function persistSavedViews(views: SavedView[]) {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(SAVED_VIEW_KEY, JSON.stringify(views));
}

function isSavedView(value: unknown): value is SavedView {
  if (!value || typeof value !== "object") {
    return false;
  }
  const item = value as Partial<SavedView>;
  return (
    typeof item.id === "string" &&
    typeof item.name === "string" &&
    typeof item.query === "string" &&
    typeof item.status === "string" &&
    typeof item.sort === "string" &&
    (item.order === "asc" || item.order === "desc") &&
    typeof item.pageSize === "number" &&
    typeof item.createdAt === "string"
  );
}

export default function IntelFilesPage() {
  const [items, setItems] = useState<IntelFileSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [query, setQuery] = useState("");
  const [appliedQuery, setAppliedQuery] = useState("");
  const [status, setStatus] = useState("");
  const [sort, setSort] = useState("updated_at");
  const [order, setOrder] = useState<"asc" | "desc">("desc");
  const [savedViews, setSavedViews] = useState<SavedView[]>([]);
  const [selectedViewId, setSelectedViewId] = useState("");
  const [viewName, setViewName] = useState("");
  const [viewMessage, setViewMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / pageSize)), [pageSize, total]);

  const loadFiles = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchIntelFiles({
        page,
        pageSize,
        status: status || undefined,
        q: appliedQuery || undefined,
        sort,
        order,
      });
      if (!result.success || !result.data) {
        setError(result.error?.message ?? "Failed to load intel files.");
        setItems([]);
        setTotal(0);
        return;
      }
      setItems(result.data.items);
      setTotal(result.data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load intel files.");
      setItems([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [appliedQuery, order, page, pageSize, sort, status]);

  useEffect(() => {
    void loadFiles();
  }, [loadFiles]);

  useEffect(() => {
    setSavedViews(loadSavedViews());
  }, []);

  function applySearch() {
    setPage(1);
    setAppliedQuery(query.trim());
    setSelectedViewId("");
  }

  function clearFilters() {
    setPage(1);
    setQuery("");
    setAppliedQuery("");
    setStatus("");
    setSort("updated_at");
    setOrder("desc");
    setSelectedViewId("");
    setViewMessage(null);
  }

  function currentFilters(): SavedViewFilters {
    return {
      query: query.trim(),
      status,
      sort,
      order,
      pageSize,
    };
  }

  function saveView() {
    const name = viewName.trim();
    if (!name) {
      setViewMessage("Name the view before saving.");
      return;
    }
    const filters = currentFilters();
    const id = name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "") || crypto.randomUUID();
    const nextView: SavedView = {
      id,
      name,
      ...filters,
      createdAt: new Date().toISOString(),
    };
    const nextViews = [
      nextView,
      ...savedViews.filter((item) => item.id !== id),
    ].slice(0, 12);
    setSavedViews(nextViews);
    persistSavedViews(nextViews);
    setSelectedViewId(nextView.id);
    setViewName("");
    setPage(1);
    setAppliedQuery(filters.query);
    setViewMessage(`Saved view: ${name}.`);
  }

  function applySavedView(viewId: string) {
    const view = savedViews.find((item) => item.id === viewId);
    if (!view) {
      setSelectedViewId("");
      return;
    }
    setSelectedViewId(view.id);
    setQuery(view.query);
    setAppliedQuery(view.query);
    setStatus(view.status);
    setSort(view.sort);
    setOrder(view.order);
    setPageSize(view.pageSize);
    setPage(1);
    setViewMessage(`Applied view: ${view.name}.`);
  }

  function deleteSavedView() {
    if (!selectedViewId) {
      return;
    }
    const view = savedViews.find((item) => item.id === selectedViewId);
    const nextViews = savedViews.filter((item) => item.id !== selectedViewId);
    setSavedViews(nextViews);
    persistSavedViews(nextViews);
    setSelectedViewId("");
    setViewMessage(view ? `Deleted view: ${view.name}.` : "Deleted saved view.");
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-medium text-cyan-300">Case workbench</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">Intel Files</h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
            Search, filter, and triage tracked intelligence cases by lifecycle status, evidence coverage, and opportunity.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void loadFiles()}
          className="rounded border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:bg-slate-900"
        >
          Refresh
        </button>
      </div>

      <div className="grid gap-3 rounded border border-slate-800 bg-slate-900/40 p-4 lg:grid-cols-[1.5fr_1fr_1fr_0.8fr_auto_auto]">
        <label className="space-y-1">
          <span className="text-xs uppercase text-slate-500">Search</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                applySearch();
              }
            }}
            className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500"
            placeholder="Title or thesis"
          />
        </label>
        <Select label="Status" value={status} onChange={(value) => { setPage(1); setStatus(value); }} options={statuses} />
        <Select label="Sort" value={sort} onChange={(value) => { setPage(1); setSort(value); }} options={sortOptions} />
        <Select
          label="Order"
          value={order}
          onChange={(value) => { setPage(1); setOrder(value as "asc" | "desc"); }}
          options={[
            { value: "desc", label: "Desc" },
            { value: "asc", label: "Asc" },
          ]}
        />
        <button
          type="button"
          onClick={applySearch}
          className="self-end rounded border border-cyan-500 bg-cyan-500 px-3 py-2 text-sm font-medium text-slate-950"
        >
          Apply
        </button>
        <button
          type="button"
          onClick={clearFilters}
          className="self-end rounded border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:bg-slate-900"
        >
          Reset
        </button>
      </div>

      <div className="grid gap-3 rounded border border-slate-800 bg-slate-900/40 p-4 lg:grid-cols-[1fr_1.2fr_auto_auto]">
        <label className="space-y-1">
          <span className="text-xs uppercase text-slate-500">Saved views</span>
          <select
            value={selectedViewId}
            onChange={(event) => applySavedView(event.target.value)}
            className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500"
          >
            <option value="">Select view</option>
            {savedViews.map((view) => (
              <option key={view.id} value={view.id}>
                {view.name}
              </option>
            ))}
          </select>
        </label>
        <label className="space-y-1">
          <span className="text-xs uppercase text-slate-500">View name</span>
          <input
            value={viewName}
            onChange={(event) => setViewName(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                saveView();
              }
            }}
            className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500"
            placeholder="High opportunity watchlist"
          />
        </label>
        <button
          type="button"
          onClick={saveView}
          className="self-end rounded border border-cyan-500 bg-cyan-500 px-3 py-2 text-sm font-medium text-slate-950"
        >
          Save View
        </button>
        <button
          type="button"
          onClick={deleteSavedView}
          disabled={!selectedViewId}
          className="self-end rounded border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Delete
        </button>
      </div>

      {viewMessage ? <p className="text-sm text-cyan-300">{viewMessage}</p> : null}

      <div className="grid gap-3 md:grid-cols-3">
        <Metric label="Matching files" value={String(total)} />
        <Metric label="Page" value={`${page} / ${totalPages}`} />
        <Metric label="Page size" value={String(pageSize)} />
      </div>

      {loading ? <p className="text-sm text-slate-400">Loading intel files...</p> : null}
      {error ? <p className="text-sm text-red-400">{error}</p> : null}

      {!loading && !error && items.length === 0 ? (
        <div className="rounded border border-dashed border-slate-800 p-6 text-sm text-slate-400">
          No intel files match the current filters.
        </div>
      ) : null}

      {!loading && !error && items.length > 0 ? (
        <div className="overflow-hidden rounded border border-slate-800">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-900 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3 font-medium">Title</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Last Seen</th>
                <th className="px-4 py-3 font-medium">Evidence</th>
                <th className="px-4 py-3 font-medium">Heat</th>
                <th className="px-4 py-3 font-medium">Opportunity</th>
                <th className="px-4 py-3 font-medium">Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {items.map((item) => (
                <tr key={item.id} className="bg-slate-950/60 hover:bg-slate-900/70">
                  <td className="px-4 py-3">
                    <Link href={`/intel-files/${item.id}`} className="font-medium text-cyan-300 hover:text-cyan-200">
                      {item.title}
                    </Link>
                    <div className="mt-1 max-w-xl truncate text-xs text-slate-500">{item.thesis ?? "No thesis recorded"}</div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded bg-slate-800 px-2 py-1 text-xs uppercase text-slate-300">
                      {item.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-400">{formatDate(item.last_seen_at)}</td>
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

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => setPage((value) => Math.max(1, value - 1))}
            className="rounded border border-slate-700 px-3 py-2 text-sm text-slate-200 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Previous
          </button>
          <button
            type="button"
            disabled={page >= totalPages}
            onClick={() => setPage((value) => Math.min(totalPages, value + 1))}
            className="rounded border border-slate-700 px-3 py-2 text-sm text-slate-200 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Next
          </button>
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-400">
          Rows
          <select
            value={pageSize}
            onChange={(event) => {
              setPage(1);
              setPageSize(Number(event.target.value));
            }}
            className="rounded border border-slate-700 bg-slate-950 px-2 py-1 text-slate-100"
          >
            {[10, 20, 50].map((value) => (
              <option key={value} value={value}>{value}</option>
            ))}
          </select>
        </label>
      </div>
    </section>
  );
}

function Select({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <label className="space-y-1">
      <span className="text-xs uppercase text-slate-500">{label}</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500"
      >
        {options.map((option) => (
          <option key={option.value || "all"} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
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
