export type ApiError = {
  code: string;
  message: string;
};

export type ApiResponse<T> = {
  success: boolean;
  data: T | null;
  error: ApiError | null;
};

export type InboxRawItem = {
  id: string;
  title: string;
  url: string | null;
  content: string | null;
  source_id: string;
  content_hash: string;
  published_at: string | null;
  captured_at: string;
};

export type InboxSubmitData = {
  raw_item: InboxRawItem;
  duplicate: boolean;
};

export type InboxListItem = {
  raw_item: InboxRawItem;
  analysis_status: "pending" | "complete";
  has_intel_file: boolean;
};

export type InboxListData = {
  items: InboxListItem[];
  total: number;
  page: number;
  page_size: number;
};

export type InboxSubmitRequest = {
  url?: string;
  title?: string;
  content?: string;
  source_id?: string | null;
};

export type SignalAnalysis = {
  id: string;
  raw_item_id: string;
  summary: string;
  signal_type: string;
  entities: unknown[];
  keywords: string[];
  claims: unknown[];
  suggested_tracking_queries: string[];
  novelty_score: number | null;
  relevance_score: number | null;
  credibility_hint: number | null;
  risk_hint: number | null;
  opportunity_types: string[];
  rationale: string | null;
  model: string | null;
  prompt_version: string | null;
  created_at: string;
};

export type AnalyzeData = {
  analysis: SignalAnalysis;
};
