"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { InboxList } from "@/components/inbox/InboxList";
import { SubmissionForm } from "@/components/inbox/SubmissionForm";
import { analyzeRawItem, createIntelFile, fetchInbox } from "@/lib/api";
import type { InboxListItem } from "@/types/inbox";

export default function InboxPage() {
  const router = useRouter();
  const [items, setItems] = useState<InboxListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [creatingId, setCreatingId] = useState<string | null>(null);

  const loadInbox = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchInbox();
      if (!result.success || !result.data) {
        setError(result.error?.message ?? "Failed to load inbox.");
        setItems([]);
        return;
      }
      setItems(result.data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load inbox.");
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadInbox();
  }, [loadInbox]);

  async function handleAnalyze(rawItemId: string) {
    setAnalyzingId(rawItemId);
    setError(null);
    try {
      const result = await analyzeRawItem(rawItemId);
      if (!result.success) {
        setError(result.error?.message ?? "Analysis failed.");
        return;
      }
      await loadInbox();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed.");
    } finally {
      setAnalyzingId(null);
    }
  }

  async function handleCreateIntelFile(rawItemId: string) {
    setCreatingId(rawItemId);
    setError(null);
    try {
      const result = await createIntelFile({ raw_item_id: rawItemId });
      if (!result.success || !result.data) {
        setError(result.error?.message ?? "Failed to create intel file.");
        return;
      }
      await loadInbox();
      router.push(`/intel-files/${result.data.intel_file.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create intel file.");
    } finally {
      setCreatingId(null);
    }
  }

  return (
    <section className="space-y-8">
      <div>
        <h1 className="text-xl font-semibold">Inbox</h1>
        <p className="mt-2 text-slate-400">
          Submit candidate signals, analyze them, then promote analyzed items into intel files.
        </p>
      </div>

      <SubmissionForm onSubmitted={loadInbox} />

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-medium">Submitted signals</h2>
          <button
            type="button"
            onClick={() => void loadInbox()}
            className="text-sm text-sky-400 hover:text-sky-300"
          >
            Refresh
          </button>
        </div>
        <InboxList
          items={items}
          loading={loading}
          error={error}
          analyzingId={analyzingId}
          creatingId={creatingId}
          onAnalyze={handleAnalyze}
          onCreateIntelFile={handleCreateIntelFile}
        />
      </div>
    </section>
  );
}
