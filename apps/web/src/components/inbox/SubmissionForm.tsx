"use client";

import { useState } from "react";

import { submitInboxItem } from "@/lib/api";
import {
  EMPTY_SUBMISSION_MESSAGE,
  hasSubmissionInput,
} from "@/lib/inbox-validation";

type Props = {
  onSubmitted: () => void;
};

export function SubmissionForm({ onSubmitted }: Props) {
  const [url, setUrl] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setMessage(null);
    setError(null);

    if (!hasSubmissionInput(url, title, content)) {
      setError(EMPTY_SUBMISSION_MESSAGE);
      return;
    }

    setLoading(true);

    try {
      const result = await submitInboxItem({
        url: url.trim() || undefined,
        title: title.trim() || undefined,
        content: content.trim() || undefined,
      });

      if (!result.success || !result.data) {
        setError(result.error?.message ?? "Submission failed.");
        return;
      }

      setMessage(
        result.data.duplicate
          ? "Duplicate detected — showing existing inbox item."
          : "Signal submitted to inbox.",
      );
      setUrl("");
      setTitle("");
      setContent("");
      onSubmitted();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Submission failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border border-slate-800 bg-slate-900 p-4">
      <div>
        <label htmlFor="url" className="mb-1 block text-sm text-slate-300">
          URL
        </label>
        <input
          id="url"
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/post"
          className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
        />
      </div>
      <div>
        <label htmlFor="title" className="mb-1 block text-sm text-slate-300">
          Title
        </label>
        <input
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Optional title"
          className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
        />
      </div>
      <div>
        <label htmlFor="content" className="mb-1 block text-sm text-slate-300">
          Content
        </label>
        <textarea
          id="content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Paste signal text"
          rows={5}
          className="w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="rounded bg-sky-600 px-4 py-2 text-sm font-medium hover:bg-sky-500 disabled:opacity-50"
      >
        {loading ? "Submitting..." : "Submit signal"}
      </button>
      {message ? <p className="text-sm text-emerald-400">{message}</p> : null}
      {error ? <p className="text-sm text-red-400">{error}</p> : null}
    </form>
  );
}
