export type SourceCheckRun = {
  id: string;
  workspace_id: string | null;
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

export type SourceProviderHealth = {
  source_hint: string;
  enabled_query_count: number;
  recent_result_count: number;
  last_result_at: string | null;
  recent_error_count: number;
  latest_error: string | null;
  recent_errors: {
    tracking_query_id: string;
    query: string;
    error: string;
  }[];
  latest_run_status: string | null;
  latest_run_error: string | null;
};

export type SourceProviderHealthData = {
  items: SourceProviderHealth[];
  total: number;
};
