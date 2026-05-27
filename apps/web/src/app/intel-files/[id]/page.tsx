"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import {
  acceptMatchSuggestion,
  attachEvidence,
  createIntelFileComment,
  fetchIntelFileComments,
  fetchIntelFileDetail,
  fetchMatchSuggestions,
  fetchTrackingQueries,
  generateTrackingQueries,
  overrideIntelFileStatus,
  updateIntelFileCollaboration,
} from "@/lib/api";
import type {
  IntelFileComment,
  IntelFileDetailData,
  MatchSuggestion,
  TrackingQuery,
} from "@/types/intel-files";

const EVIDENCE_TYPES = [
  "follow_up",
  "corroboration",
  "contradiction",
  "correction",
  "noise",
] as const;

const STATUS_OPTIONS = [
  "new",
  "watching",
  "spreading",
  "validating",
  "cooling",
  "dormant",
  "resurrected",
  "verified",
  "debunked",
  "noise",
  "archived",
] as const;

function formatScore(value: number | null) {
  return value === null ? "—" : value.toFixed(1);
}

function formatOptionalDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : "Never";
}

export default function IntelFileDetailPage() {
  const params = useParams<{ id: string }>();
  const [detail, setDetail] = useState<IntelFileDetailData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<MatchSuggestion[]>([]);
  const [comments, setComments] = useState<IntelFileComment[]>([]);
  const [trackingQueries, setTrackingQueries] = useState<TrackingQuery[]>([]);
  const [trackingQueryError, setTrackingQueryError] = useState<string | null>(null);
  const [generatingTrackingQueries, setGeneratingTrackingQueries] = useState(false);
  const [suggestionsError, setSuggestionsError] = useState<string | null>(null);
  const [acceptingSuggestionId, setAcceptingSuggestionId] = useState<string | null>(null);
  const [attachError, setAttachError] = useState<string | null>(null);
  const [attaching, setAttaching] = useState(false);
  const [rawItemId, setRawItemId] = useState("");
  const [evidenceType, setEvidenceType] = useState<(typeof EVIDENCE_TYPES)[number]>("follow_up");
  const [confidence, setConfidence] = useState("0.8");
  const [attachedBy, setAttachedBy] = useState<"user" | "system">("user");
  const [rationale, setRationale] = useState("");
  const [overrideStatus, setOverrideStatus] = useState<(typeof STATUS_OPTIONS)[number]>("watching");
  const [overrideReason, setOverrideReason] = useState("");
  const [overrideError, setOverrideError] = useState<string | null>(null);
  const [overriding, setOverriding] = useState(false);
  const [ownerUserId, setOwnerUserId] = useState("");
  const [reviewNote, setReviewNote] = useState("");
  const [collaborationError, setCollaborationError] = useState<string | null>(null);
  const [savingCollaboration, setSavingCollaboration] = useState(false);
  const [commentBody, setCommentBody] = useState("");
  const [commentError, setCommentError] = useState<string | null>(null);
  const [savingComment, setSavingComment] = useState(false);

  const loadDetail = useCallback(async () => {
    if (!params.id) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await fetchIntelFileDetail(params.id);
      if (!result.success || !result.data) {
        setError(result.error?.message ?? "Failed to load intel file.");
        setDetail(null);
        return;
      }
      setDetail(result.data);
      setOwnerUserId(result.data.intel_file.owner_user_id ?? "");
      setReviewNote(result.data.intel_file.review_note ?? "");
      const [suggestionsResult, commentsResult, trackingQueriesResult] = await Promise.all([
        fetchMatchSuggestions(params.id),
        fetchIntelFileComments(params.id),
        fetchTrackingQueries(params.id),
      ]);
      if (suggestionsResult.success && suggestionsResult.data) {
        setSuggestions(suggestionsResult.data.items);
        setSuggestionsError(null);
      } else {
        setSuggestions([]);
        setSuggestionsError(suggestionsResult.error?.message ?? "Failed to load suggestions.");
      }
      setComments(commentsResult.success && commentsResult.data ? commentsResult.data.items : []);
      if (trackingQueriesResult.success && trackingQueriesResult.data) {
        setTrackingQueries(trackingQueriesResult.data.items);
        setTrackingQueryError(null);
      } else {
        setTrackingQueries([]);
        setTrackingQueryError(
          trackingQueriesResult.error?.message ?? "Failed to load tracking queries.",
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load intel file.");
      setDetail(null);
      setSuggestions([]);
      setComments([]);
      setTrackingQueries([]);
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    void loadDetail();
  }, [loadDetail]);

  async function handleAttachEvidence(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!params.id || !rawItemId.trim()) {
      setAttachError("Raw item ID is required.");
      return;
    }

    setAttaching(true);
    setAttachError(null);
    try {
      const parsedConfidence = confidence.trim() ? Number(confidence) : null;
      const result = await attachEvidence(params.id, {
        raw_item_id: rawItemId.trim(),
        evidence_type: evidenceType,
        confidence: Number.isFinite(parsedConfidence) ? parsedConfidence : null,
        attached_by: attachedBy,
        rationale: rationale.trim() || null,
      });
      if (!result.success) {
        setAttachError(result.error?.message ?? "Failed to attach evidence.");
        return;
      }
      setRawItemId("");
      setRationale("");
      await loadDetail();
    } catch (err) {
      setAttachError(err instanceof Error ? err.message : "Failed to attach evidence.");
    } finally {
      setAttaching(false);
    }
  }

  async function handleAcceptSuggestion(suggestion: MatchSuggestion) {
    setAcceptingSuggestionId(suggestion.id);
    setSuggestionsError(null);
    try {
      const result = await acceptMatchSuggestion(suggestion.id, suggestion.rationale);
      if (!result.success) {
        setSuggestionsError(result.error?.message ?? "Failed to accept suggestion.");
        return;
      }
      await loadDetail();
    } catch (err) {
      setSuggestionsError(err instanceof Error ? err.message : "Failed to accept suggestion.");
    } finally {
      setAcceptingSuggestionId(null);
    }
  }

  async function handleOverrideStatus(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!params.id || !overrideReason.trim()) {
      setOverrideError("Reason is required.");
      return;
    }

    setOverriding(true);
    setOverrideError(null);
    try {
      const result = await overrideIntelFileStatus(params.id, {
        status: overrideStatus,
        reason: overrideReason.trim(),
      });
      if (!result.success) {
        setOverrideError(result.error?.message ?? "Failed to override status.");
        return;
      }
      setOverrideReason("");
      await loadDetail();
    } catch (err) {
      setOverrideError(err instanceof Error ? err.message : "Failed to override status.");
    } finally {
      setOverriding(false);
    }
  }

  async function handleSaveCollaboration(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!params.id) {
      return;
    }
    setSavingCollaboration(true);
    setCollaborationError(null);
    try {
      const result = await updateIntelFileCollaboration(params.id, {
        owner_user_id: ownerUserId.trim() || null,
        review_note: reviewNote.trim() || null,
        mark_reviewed: true,
      });
      if (!result.success) {
        setCollaborationError(result.error?.message ?? "Failed to save review.");
        return;
      }
      await loadDetail();
    } catch (err) {
      setCollaborationError(err instanceof Error ? err.message : "Failed to save review.");
    } finally {
      setSavingCollaboration(false);
    }
  }

  async function handleCreateComment(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!params.id || !commentBody.trim()) {
      setCommentError("Comment is required.");
      return;
    }
    setSavingComment(true);
    setCommentError(null);
    try {
      const result = await createIntelFileComment(params.id, commentBody.trim());
      if (!result.success) {
        setCommentError(result.error?.message ?? "Failed to add comment.");
        return;
      }
      setCommentBody("");
      await loadDetail();
    } catch (err) {
      setCommentError(err instanceof Error ? err.message : "Failed to add comment.");
    } finally {
      setSavingComment(false);
    }
  }

  async function handleGenerateTrackingQueries(regenerate = false) {
    if (!params.id) {
      return;
    }
    setGeneratingTrackingQueries(true);
    setTrackingQueryError(null);
    try {
      const result = await generateTrackingQueries(params.id, 12, regenerate);
      if (!result.success || !result.data) {
        setTrackingQueryError(result.error?.message ?? "Failed to generate tracking queries.");
        return;
      }
      setTrackingQueries(result.data.items);
    } catch (err) {
      setTrackingQueryError(
        err instanceof Error ? err.message : "Failed to generate tracking queries.",
      );
    } finally {
      setGeneratingTrackingQueries(false);
    }
  }

  if (loading) {
    return <p className="text-sm text-slate-400">Loading intel file...</p>;
  }

  if (error || !detail) {
    return (
      <section className="space-y-4">
        <Link href="/intel-files" className="text-sm text-sky-400 hover:text-sky-300">
          Back to Intel Files
        </Link>
        <p className="text-sm text-red-400">{error ?? "Intel file not found."}</p>
      </section>
    );
  }

  const file = detail.intel_file;

  return (
    <section className="space-y-8">
      <div className="space-y-2">
        <Link href="/intel-files" className="text-sm text-sky-400 hover:text-sky-300">
          Back to Intel Files
        </Link>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-xl font-semibold">{file.title}</h1>
          <span className="rounded bg-slate-800 px-2 py-1 text-xs uppercase text-slate-300">
            {file.status}
          </span>
        </div>
        <p className="text-slate-300">{file.thesis ?? "No thesis recorded."}</p>
        <p className="text-sm text-slate-400">
          First seen {new Date(file.first_seen_at).toLocaleString()} · Last seen{" "}
          {new Date(file.last_seen_at).toLocaleString()} · Evidence {file.evidence_count} · Sources{" "}
          {file.source_count}
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-5">
        {[
          ["Novelty", detail.novelty_score],
          ["Heat", file.heat_score],
          ["Credibility", file.credibility_score],
          ["Opportunity", file.opportunity_score],
          ["Risk", file.risk_score],
        ].map(([label, value]) => (
          <div key={label} className="rounded-lg border border-slate-800 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
            <p className="mt-2 text-lg font-medium">{formatScore(value as number | null)}</p>
          </div>
        ))}
      </div>

      <div className="rounded-lg border border-slate-800 p-4">
        <h2 className="text-lg font-medium">Status override</h2>
        <form onSubmit={(event) => void handleOverrideStatus(event)} className="mt-4 space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block text-sm">
              <span className="text-slate-400">Status</span>
              <select
                value={overrideStatus}
                onChange={(event) =>
                  setOverrideStatus(event.target.value as (typeof STATUS_OPTIONS)[number])
                }
                className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              >
                {STATUS_OPTIONS.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-sm">
              <span className="text-slate-400">Reason</span>
              <input
                value={overrideReason}
                onChange={(event) => setOverrideReason(event.target.value)}
                className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
                placeholder="Why this status is correct."
              />
            </label>
          </div>
          {overrideError ? <p className="text-sm text-red-400">{overrideError}</p> : null}
          <button
            type="submit"
            disabled={overriding}
            className="rounded border border-slate-700 px-3 py-2 text-sm text-sky-300 hover:bg-slate-800 disabled:opacity-50"
          >
            {overriding ? "Saving..." : "Save override"}
          </button>
        </form>
      </div>

      <div className="rounded-lg border border-slate-800 p-4">
        <h2 className="text-lg font-medium">Team review</h2>
        <form onSubmit={(event) => void handleSaveCollaboration(event)} className="mt-4 space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block text-sm">
              <span className="text-slate-400">Owner user ID</span>
              <input
                value={ownerUserId}
                onChange={(event) => setOwnerUserId(event.target.value)}
                className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
                placeholder="User UUID"
              />
            </label>
            <div className="text-sm text-slate-400">
              <span>Last reviewed</span>
              <p className="mt-3 text-slate-300">
                {file.last_reviewed_at ? new Date(file.last_reviewed_at).toLocaleString() : "Not reviewed"}
              </p>
            </div>
          </div>
          <label className="block text-sm">
            <span className="text-slate-400">Review note</span>
            <textarea
              value={reviewNote}
              onChange={(event) => setReviewNote(event.target.value)}
              className="mt-1 min-h-20 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            />
          </label>
          {collaborationError ? <p className="text-sm text-red-400">{collaborationError}</p> : null}
          <button
            type="submit"
            disabled={savingCollaboration}
            className="rounded border border-slate-700 px-3 py-2 text-sm text-sky-300 hover:bg-slate-800 disabled:opacity-50"
          >
            {savingCollaboration ? "Saving..." : "Save review"}
          </button>
        </form>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <h2 className="text-lg font-medium">Entities</h2>
          {file.entities.length === 0 ? (
            <p className="mt-2 text-sm text-slate-400">No entities extracted.</p>
          ) : (
            <ul className="mt-2 space-y-2 text-sm text-slate-300">
              {file.entities.map((entity, index) => (
                <li key={index} className="rounded border border-slate-800 px-3 py-2">
                  {typeof entity === "object" && entity !== null && "name" in entity
                    ? String((entity as { name?: string }).name)
                    : JSON.stringify(entity)}
                </li>
              ))}
            </ul>
          )}
        </div>
        <div>
          <h2 className="text-lg font-medium">Keywords</h2>
          {file.keywords.length === 0 ? (
            <p className="mt-2 text-sm text-slate-400">No keywords extracted.</p>
          ) : (
            <div className="mt-2 flex flex-wrap gap-2">
              {file.keywords.map((keyword) => (
                <span key={keyword} className="rounded bg-slate-800 px-2 py-1 text-xs text-slate-300">
                  {keyword}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="rounded-lg border border-slate-800 p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-medium">Tracking queries</h2>
            <p className="mt-1 text-sm text-slate-400">
              {trackingQueries.length} active {trackingQueries.length === 1 ? "query" : "queries"} ·{" "}
              {trackingQueries.filter((item) => item.last_checked_at === null).length} never checked
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              disabled={generatingTrackingQueries}
              onClick={() => void handleGenerateTrackingQueries(false)}
              className="rounded border border-slate-700 px-3 py-2 text-sm text-sky-300 hover:bg-slate-800 disabled:opacity-50"
            >
              {generatingTrackingQueries ? "Generating..." : "Generate"}
            </button>
            {trackingQueries.length > 0 ? (
              <button
                type="button"
                disabled={generatingTrackingQueries}
                onClick={() => void handleGenerateTrackingQueries(true)}
                className="rounded border border-slate-700 px-3 py-2 text-sm text-amber-300 hover:bg-slate-800 disabled:opacity-50"
              >
                Regenerate
              </button>
            ) : null}
          </div>
        </div>
        {trackingQueryError ? <p className="mt-3 text-sm text-red-400">{trackingQueryError}</p> : null}
        {trackingQueries.length === 0 ? (
          <p className="mt-4 text-sm text-slate-400">No tracking queries generated.</p>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-3 py-2">Query</th>
                  <th className="px-3 py-2">Source</th>
                  <th className="px-3 py-2">Last checked</th>
                  <th className="px-3 py-2">State</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {trackingQueries.map((item) => (
                  <tr key={item.id}>
                    <td className="max-w-xl px-3 py-3 align-top">
                      <p className="font-medium text-slate-200">{item.query}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {item.rationale ?? "No rationale recorded."}
                      </p>
                    </td>
                    <td className="px-3 py-3 align-top text-slate-300">
                      {item.source_hint ?? "search"}
                    </td>
                    <td className="px-3 py-3 align-top text-slate-300">
                      {formatOptionalDate(item.last_checked_at)}
                    </td>
                    <td className="px-3 py-3 align-top">
                      <span
                        className={`rounded px-2 py-1 text-xs ${
                          item.enabled
                            ? "bg-emerald-950 text-emerald-300"
                            : "bg-slate-800 text-slate-400"
                        }`}
                      >
                        {item.enabled ? "Enabled" : "Disabled"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="rounded-lg border border-slate-800 p-4">
        <h2 className="text-lg font-medium">Attach evidence</h2>
        <p className="mt-1 text-sm text-slate-400">
          Paste a RawItem ID from the inbox to attach follow-up evidence manually.
        </p>
        <form onSubmit={(event) => void handleAttachEvidence(event)} className="mt-4 space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block text-sm">
              <span className="text-slate-400">Raw item ID</span>
              <input
                value={rawItemId}
                onChange={(event) => setRawItemId(event.target.value)}
                className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
                placeholder="00000000-0000-0000-0000-000000000000"
              />
            </label>
            <label className="block text-sm">
              <span className="text-slate-400">Evidence type</span>
              <select
                value={evidenceType}
                onChange={(event) =>
                  setEvidenceType(event.target.value as (typeof EVIDENCE_TYPES)[number])
                }
                className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              >
                {EVIDENCE_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-sm">
              <span className="text-slate-400">Confidence</span>
              <input
                value={confidence}
                onChange={(event) => setConfidence(event.target.value)}
                className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
                placeholder="0.8"
              />
            </label>
            <label className="block text-sm">
              <span className="text-slate-400">Attached by</span>
              <select
                value={attachedBy}
                onChange={(event) => setAttachedBy(event.target.value as "user" | "system")}
                className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              >
                <option value="user">user</option>
                <option value="system">system</option>
              </select>
            </label>
          </div>
          <label className="block text-sm">
            <span className="text-slate-400">Rationale</span>
            <textarea
              value={rationale}
              onChange={(event) => setRationale(event.target.value)}
              className="mt-1 min-h-24 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              placeholder="Why this evidence belongs to the file."
            />
          </label>
          {attachError ? <p className="text-sm text-red-400">{attachError}</p> : null}
          <button
            type="submit"
            disabled={attaching}
            className="rounded border border-slate-700 px-3 py-2 text-sm text-emerald-300 hover:bg-slate-800 disabled:opacity-50"
          >
            {attaching ? "Attaching..." : "Attach evidence"}
          </button>
        </form>
      </div>

      <div>
        <h2 className="text-lg font-medium">Match suggestions</h2>
        {suggestionsError ? <p className="mt-2 text-sm text-red-400">{suggestionsError}</p> : null}
        {suggestions.length === 0 ? (
          <p className="mt-2 text-sm text-slate-400">No open match suggestions.</p>
        ) : (
          <ul className="mt-2 space-y-3">
            {suggestions.map((item) => (
              <li key={item.id} className="rounded border border-slate-800 px-4 py-3 text-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium text-slate-200">{item.result_title}</span>
                  <span className="rounded bg-emerald-950 px-2 py-1 text-xs text-emerald-300">
                    {Math.round(item.confidence * 100)}%
                  </span>
                  <span className="text-xs text-slate-500">
                    {item.source_name ?? "unknown source"}
                  </span>
                </div>
                <p className="mt-1 text-slate-400">{item.result_snippet ?? "No snippet."}</p>
                <p className="mt-1 text-xs text-slate-500">{item.rationale}</p>
                {item.result_url ? (
                  <a
                    href={item.result_url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-2 inline-block text-xs text-sky-400 hover:text-sky-300"
                  >
                    Open source result
                  </a>
                ) : null}
                <div className="mt-3">
                  <button
                    type="button"
                    disabled={acceptingSuggestionId === item.id}
                    onClick={() => void handleAcceptSuggestion(item)}
                    className="rounded border border-emerald-800 px-3 py-2 text-xs text-emerald-300 hover:bg-emerald-950 disabled:opacity-50"
                  >
                    {acceptingSuggestionId === item.id ? "Accepting..." : "Accept suggestion"}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div>
        <h2 className="text-lg font-medium">Comments</h2>
        <form onSubmit={(event) => void handleCreateComment(event)} className="mt-2 space-y-3">
          <textarea
            value={commentBody}
            onChange={(event) => setCommentBody(event.target.value)}
            className="min-h-20 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
            placeholder="Add a team note."
          />
          {commentError ? <p className="text-sm text-red-400">{commentError}</p> : null}
          <button
            type="submit"
            disabled={savingComment}
            className="rounded border border-slate-700 px-3 py-2 text-sm text-sky-300 hover:bg-slate-800 disabled:opacity-50"
          >
            {savingComment ? "Adding..." : "Add comment"}
          </button>
        </form>
        {comments.length === 0 ? (
          <p className="mt-3 text-sm text-slate-400">No comments yet.</p>
        ) : (
          <ul className="mt-3 space-y-3">
            {comments.map((comment) => (
              <li key={comment.id} className="rounded border border-slate-800 px-4 py-3 text-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium text-slate-200">{comment.author_name}</span>
                  <span className="text-xs text-slate-500">{comment.author_email}</span>
                  <span className="text-xs text-slate-500">
                    {new Date(comment.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="mt-2 text-slate-300">{comment.body}</p>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div>
        <h2 className="text-lg font-medium">Evidence</h2>
        {detail.evidence.length === 0 ? (
          <p className="mt-2 text-sm text-slate-400">No evidence attached yet.</p>
        ) : (
          <ul className="mt-2 space-y-3">
            {detail.evidence.map((item) => (
              <li key={item.id} className="rounded border border-slate-800 px-4 py-3 text-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium text-slate-200">{item.evidence_type}</span>
                  <span className="text-xs text-slate-500">raw item {item.raw_item_id}</span>
                  <span className="text-xs text-slate-500">by {item.attached_by}</span>
                </div>
                <p className="mt-1 text-slate-400">{item.rationale ?? "No rationale provided."}</p>
                <p className="mt-1 text-xs text-slate-500">
                  Confidence {formatScore(item.confidence)} ·{" "}
                  {new Date(item.attached_at).toLocaleString()}
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div>
        <h2 className="text-lg font-medium">Timeline</h2>
        {detail.timeline.length === 0 ? (
          <p className="mt-2 text-sm text-slate-400">No timeline events yet.</p>
        ) : (
          <ul className="mt-2 space-y-3">
            {detail.timeline.map((event) => (
              <li key={event.id} className="rounded border border-slate-800 px-4 py-3 text-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium text-slate-200">{event.title}</span>
                  <span className="text-xs uppercase text-slate-500">{event.event_type}</span>
                </div>
                <p className="mt-1 text-slate-400">{event.description}</p>
                <p className="mt-1 text-xs text-slate-500">
                  {new Date(event.event_time).toLocaleString()}
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
