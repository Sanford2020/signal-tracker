export type IntelFileSummary = {
  id: string;
  workspace_id: string | null;
  owner_user_id: string | null;
  title: string;
  thesis: string | null;
  status: string;
  first_seen_at: string;
  last_seen_at: string;
  primary_signal_type: string | null;
  entities: unknown[];
  keywords: string[];
  source_count: number;
  evidence_count: number;
  heat_score: number | null;
  credibility_score: number | null;
  opportunity_score: number | null;
  risk_score: number | null;
  review_note: string | null;
  last_reviewed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type IntelFileCreateRequest = {
  raw_item_id: string;
  analysis_id?: string;
  title?: string;
  thesis?: string;
};

export type IntelFileCreateData = {
  intel_file: IntelFileSummary;
};

export type IntelFileListData = {
  items: IntelFileSummary[];
  total: number;
  page: number;
  page_size: number;
};

export type IntelFileSavedViewFilters = {
  query: string;
  status: string;
  sort: string;
  order: "asc" | "desc";
  page_size: number;
};

export type IntelFileSavedView = {
  id: string;
  workspace_id: string | null;
  name: string;
  slug: string;
  filters: IntelFileSavedViewFilters;
  created_by_email: string | null;
  created_at: string;
  updated_at: string;
};

export type IntelFileSavedViewListData = {
  items: IntelFileSavedView[];
  total: number;
};

export type IntelFileSavedViewData = {
  item: IntelFileSavedView;
};

export type IntelFileSavedViewDeleteData = {
  deleted_id: string;
};

export type EvidenceSummary = {
  id: string;
  intel_file_id: string;
  raw_item_id: string;
  evidence_type: string;
  confidence: number | null;
  attached_by: string;
  rationale: string | null;
  attached_at: string;
};

export type EvidenceAttachRequest = {
  raw_item_id: string;
  evidence_type?: string;
  confidence?: number | null;
  attached_by?: string;
  rationale?: string | null;
};

export type EvidenceAttachData = {
  evidence: EvidenceSummary;
  intel_file: IntelFileSummary;
};

export type IntelEventSummary = {
  id: string;
  intel_file_id: string;
  event_type: string;
  event_time: string;
  title: string;
  description: string | null;
  source_evidence_id: string | null;
};

export type IntelFileDetailData = {
  intel_file: IntelFileSummary;
  novelty_score: number | null;
  evidence: EvidenceSummary[];
  timeline: IntelEventSummary[];
  snapshots: unknown[];
  alerts: unknown[];
};

export type MatchSuggestion = {
  id: string;
  intel_file_id: string;
  source_check_result_id: string;
  suggested_evidence_type: string;
  confidence: number;
  rationale: string;
  status: string;
  created_at: string;
  decided_at: string | null;
  result_title: string;
  result_url: string | null;
  result_snippet: string | null;
  source_name: string | null;
};

export type MatchSuggestionListData = {
  items: MatchSuggestion[];
  total: number;
};

export type MatchSuggestionGenerateData = {
  items: MatchSuggestion[];
  created_count: number;
};

export type MatchSuggestionAcceptData = {
  item: MatchSuggestion;
  raw_item_id: string;
  evidence_id: string;
  duplicate_raw_item: boolean;
};

export type MatchSuggestionStatusUpdateData = {
  item: MatchSuggestion;
};

export type StatusOverrideRequest = {
  status: string;
  reason: string;
};

export type StatusOverrideData = {
  previous_status: string;
  next_status: string;
  reason: string;
};

export type CollaborationUpdateRequest = {
  owner_user_id?: string | null;
  review_note?: string | null;
  mark_reviewed?: boolean;
};

export type CollaborationRead = {
  intel_file_id: string;
  owner_user_id: string | null;
  review_note: string | null;
  last_reviewed_at: string | null;
};

export type CollaborationData = {
  item: CollaborationRead;
};

export type IntelFileComment = {
  id: string;
  intel_file_id: string;
  author_user_id: string;
  author_email: string;
  author_name: string;
  body: string;
  created_at: string;
};

export type CommentListData = {
  items: IntelFileComment[];
  total: number;
};

export type CommentCreateData = {
  item: IntelFileComment;
};
