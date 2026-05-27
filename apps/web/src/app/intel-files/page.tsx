"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import {
  deleteIntelFileSavedView,
  fetchIntelFiles,
  fetchIntelFileSavedViews,
  saveIntelFileSavedView,
  updateIntelFileSavedView,
} from "@/lib/api";
import type { IntelFileSavedView, IntelFileSavedViewFilters, IntelFileSummary } from "@/types/intel-files";

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
  const [savedViews, setSavedViews] = useState<IntelFileSavedView[]>([]);
  const [selectedViewId, setSelectedViewId] = useState("");
  const [viewName, setViewName] = useState("");
  const [viewMessage, setViewMessage] = useState<string | null>(null);
  const [savedViewsLoading, setSavedViewsLoading] = useState(true);
  const [savingView, setSavingView] = useState(false);
  const [updatingView, setUpdatingView] = useState(false);
  const [deletingView, setDeletingView] = useState(false);
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
    async function loadSavedViews() {
      setSavedViewsLoading(true);
      try {
        const result = await fetchIntelFileSavedViews();
        if (!result.success || !result.data) {
          setViewMessage(result.error?.message ?? "Failed to load saved views.");
          return;
        }
        setSavedViews(result.data.items);
      } catch (err) {
        setViewMessage(err instanceof Error ? err.message : "Failed to load saved views.");
      } finally {
        setSavedViewsLoading(false);
      }
    }
    void loadSavedViews();
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
    setViewName("");
    setViewMessage(null);
  }

  function currentFilters(): IntelFileSavedViewFilters {
    return {
      query: query.trim(),
      status,
      sort,
      order,
      page_size: pageSize,
    };
  }

  async function saveView() {
    const name = viewName.trim();
    if (!name) {
      setViewMessage("Name the view before saving.");
      return;
    }
    const filters = currentFilters();
    setSavingView(true);
    try {
      const result = await saveIntelFileSavedView(name, filters);
      if (!result.success || !result.data) {
        setViewMessage(result.error?.message ?? "Failed to save view.");
        return;
      }
      const savedView = result.data.item;
      setSavedViews((views) => [
        savedView,
        ...views.filter((item) => item.id !== savedView.id),
      ]);
      setSelectedViewId(savedView.id);
      setViewName("");
      setPage(1);
      setAppliedQuery(filters.query);
      setViewMessage(`Saved shared view: ${name}.`);
    } catch (err) {
      setViewMessage(err instanceof Error ? err.message : "Failed to save view.");
    } finally {
      setSavingView(false);
    }
  }

  async function updateSelectedView() {
    if (!selectedViewId) {
      return;
    }
    const selectedView = savedViews.find((item) => item.id === selectedViewId);
    const name = viewName.trim() || selectedView?.name;
    if (!name) {
      setViewMessage("Name the view before updating.");
      return;
    }
    const filters = currentFilters();
    setUpdatingView(true);
    try {
      const result = await updateIntelFileSavedView(selectedViewId, { name, filters });
      if (!result.success || !result.data) {
        setViewMessage(result.error?.message ?? "Failed to update view.");
        return;
      }
      const updatedView = result.data.item;
      setSavedViews((views) => [
        updatedView,
        ...views.filter((item) => item.id !== updatedView.id),
      ]);
      setSelectedViewId(updatedView.id);
      setViewName(updatedView.name);
      setPage(1);
      setAppliedQuery(filters.query);
      setViewMessage(`Updated shared view: ${updatedView.name}.`);
    } catch (err) {
      setViewMessage(err instanceof Error ? err.message : "Failed to update view.");
    } finally {
      setUpdatingView(false);
    }
  }

  function applySavedView(viewId: string) {
    const view = savedViews.find((item) => item.id === viewId);
    if (!view) {
      setSelectedViewId("");
      setViewName("");
      return;
    }
    setSelectedViewId(view.id);
    setViewName(view.name);
    setQuery(view.filters.query);
    setAppliedQuery(view.filters.query);
    setStatus(view.filters.status);
    setSort(view.filters.sort);
    setOrder(view.filters.order);
    setPageSize(view.filters.page_size);
    setPage(1);
    setViewMessage(`Applied view: ${view.name}.`);
  }

  async function deleteSavedView() {
    if (!selectedViewId) {
      return;
    }
    const view = savedViews.find((item) => item.id === selectedViewId);
    setDeletingView(true);
    try {
      const result = await deleteIntelFileSavedView(selectedViewId);
      if (!result.success || !result.data) {
        setViewMessage(result.error?.message ?? "Failed to delete view.");
        return;
      }
      setSavedViews((views) => views.filter((item) => item.id !== selectedViewId));
      setSelectedViewId("");
      setViewName("");
      setViewMessage(view ? `Deleted shared view: ${view.name}.` : "Deleted saved view.");
    } catch (err) {
      setViewMessage(err instanceof Error ? err.message : "Failed to delete view.");
    } finally {
      setDeletingView(false);
    }
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

      <div className="grid gap-3 rounded border border-slate-800 bg-slate-900/40 p-4 lg:grid-cols-[1fr_1.2fr_auto_auto_auto]">
        <label className="space-y-1">
          <span className="text-xs uppercase text-slate-500">Saved views</span>
          <select
            value={selectedViewId}
            onChange={(event) => applySavedView(event.target.value)}
            disabled={savedViewsLoading || savingView || updatingView || deletingView}
            className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500"
          >
            <option value="">{savedViewsLoading ? "Loading views..." : "Select view"}</option>
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
                if (selectedViewId) {
                  void updateSelectedView();
                } else {
                  void saveView();
                }
              }
            }}
            disabled={savingView || updatingView || deletingView}
            className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-500"
            placeholder="High opportunity watchlist"
          />
        </label>
        <button
          type="button"
          onClick={() => void saveView()}
          disabled={savingView || updatingView || deletingView || savedViewsLoading}
          className="self-end rounded border border-cyan-500 bg-cyan-500 px-3 py-2 text-sm font-medium text-slate-950 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {savingView ? "Saving..." : "Save View"}
        </button>
        <button
          type="button"
          onClick={() => void updateSelectedView()}
          disabled={!selectedViewId || savingView || updatingView || deletingView || savedViewsLoading}
          className="self-end rounded border border-emerald-500 bg-emerald-500 px-3 py-2 text-sm font-medium text-slate-950 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {updatingView ? "Updating..." : "Update Selected"}
        </button>
        <button
          type="button"
          onClick={() => void deleteSavedView()}
          disabled={!selectedViewId || savingView || updatingView || deletingView || savedViewsLoading}
          className="self-end rounded border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {deletingView ? "Deleting..." : "Delete"}
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
