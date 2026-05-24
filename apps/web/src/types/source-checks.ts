export type SourceCheckRun = {
  id: string;
  status: string;
  checked_query_count: number;
  result_count: number;
  error: string | null;
  started_at: string;
  finished_at: string | null;
};

export type SourceCheckResult = {
  id: string;
  run_id: string;
  tracking_query_id: string;
  title: string;
  url: string | null;
  snippet: string | null;
  source_name: string | null;
  source_hint: string | null;
  raw: Record<string, unknown> | null;
  checked_at: string;
};

export type SourceCheckRunData = {
  run: SourceCheckRun;
  results: SourceCheckResult[];
};

export type SourceCheckRunListData = {
  items: SourceCheckRun[];
  total: number;
};
