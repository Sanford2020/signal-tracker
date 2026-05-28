import type {
  AnalyzeData,
  ApiResponse,
  InboxListData,
  InboxSubmitData,
  InboxSubmitRequest,
} from "@/types/inbox";
import type {
  AlertListData,
  AlertSeverityFilter,
  AlertStatusFilter,
  AlertSummary,
  AlertUpdateRequest,
} from "@/types/alerts";
import type { DailyBriefingData, WeeklyRetrospectiveData } from "@/types/briefings";
import type {
  BootstrapData,
  BootstrapRequest,
  WorkspaceListData,
  WorkspaceMemberCreateData,
  WorkspaceMemberCreateRequest,
  WorkspaceMemberListData,
  AuditEventListData,
} from "@/types/auth";
import type {
  EvidenceAttachData,
  EvidenceAttachRequest,
  CollaborationData,
  CollaborationUpdateRequest,
  CommentCreateData,
  CommentListData,
  IntelFileCreateData,
  IntelFileCreateRequest,
  IntelFileDetailData,
  IntelFileListData,
  IntelFileSavedViewData,
  IntelFileSavedViewDeleteData,
  IntelFileSavedViewFilters,
  IntelFileSavedViewListData,
  IntelFileSavedViewUpdateRequest,
  MatchSuggestionAcceptData,
  MatchSuggestionGenerateData,
  MatchSuggestionListData,
  MatchSuggestionStatusUpdateData,
  StatusOverrideData,
  StatusOverrideRequest,
  TrackingQueryGenerateData,
  TrackingQueryListData,
  TrackingQueryUpdateData,
} from "@/types/intel-files";
import type { SourceCheckRunData, SourceCheckRunListData, SourceProviderHealthData } from "@/types/source-checks";

import { extractErrorMessage } from "@/lib/inbox-validation";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function workspaceHeaders(): Record<string, string> {
  if (typeof window === "undefined") {
    return {};
  }
  const workspaceId = window.localStorage.getItem("signal-tracker:workspace-id");
  const userEmail = window.localStorage.getItem("signal-tracker:user-email");
  const userToken = window.localStorage.getItem("signal-tracker:user-token");
  return {
    ...(workspaceId ? { "X-Workspace-Id": workspaceId } : {}),
    ...(userEmail ? { "X-User-Email": userEmail } : {}),
    ...(userToken ? { "X-User-Token": userToken } : {}),
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<ApiResponse<T>> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...workspaceHeaders(),
      ...(init?.headers ?? {}),
    },
  });

  const body: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const message = extractErrorMessage(body, response.status);
    if (response.status === 400 || response.status === 422 || response.status === 409) {
      return {
        success: false,
        data: null,
        error: {
          code: response.status === 409 ? "conflict" : "validation_error",
          message,
        },
      };
    }
    throw new Error(message);
  }

  return body as ApiResponse<T>;
}

export async function submitInboxItem(body: InboxSubmitRequest) {
  return request<InboxSubmitData>("/api/v1/inbox/submit", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function fetchInbox(page = 1, pageSize = 20) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<InboxListData>(`/api/v1/inbox?${params.toString()}`);
}

export async function analyzeRawItem(rawItemId: string) {
  return request<AnalyzeData>(`/api/v1/raw-items/${rawItemId}/analyze`, {
    method: "POST",
  });
}

export async function createIntelFile(body: IntelFileCreateRequest) {
  return request<IntelFileCreateData>("/api/v1/intel-files", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export type IntelFileListOptions = {
  page?: number;
  pageSize?: number;
  status?: string;
  q?: string;
  sort?: string;
  order?: "asc" | "desc";
};

export async function fetchIntelFiles(pageOrOptions: number | IntelFileListOptions = 1, pageSize = 20) {
  const options: IntelFileListOptions =
    typeof pageOrOptions === "number" ? { page: pageOrOptions, pageSize } : pageOrOptions;
  const params = new URLSearchParams({
    page: String(options.page ?? 1),
    page_size: String(options.pageSize ?? 20),
  });
  if (options.status) {
    params.set("status", options.status);
  }
  if (options.q) {
    params.set("q", options.q);
  }
  if (options.sort) {
    params.set("sort", options.sort);
  }
  if (options.order) {
    params.set("order", options.order);
  }
  return request<IntelFileListData>(`/api/v1/intel-files?${params.toString()}`);
}

export async function fetchIntelFileSavedViews() {
  return request<IntelFileSavedViewListData>("/api/v1/intel-file-saved-views");
}

export async function saveIntelFileSavedView(
  name: string,
  filters: IntelFileSavedViewFilters,
  description = "",
  isDefault = false,
) {
  return request<IntelFileSavedViewData>("/api/v1/intel-file-saved-views", {
    method: "POST",
    body: JSON.stringify({ name, description, filters, is_default: isDefault }),
  });
}

export async function deleteIntelFileSavedView(viewId: string) {
  return request<IntelFileSavedViewDeleteData>(`/api/v1/intel-file-saved-views/${viewId}`, {
    method: "DELETE",
  });
}

export async function updateIntelFileSavedView(viewId: string, body: IntelFileSavedViewUpdateRequest) {
  return request<IntelFileSavedViewData>(`/api/v1/intel-file-saved-views/${viewId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function markIntelFileSavedViewUsed(viewId: string) {
  return request<IntelFileSavedViewData>(`/api/v1/intel-file-saved-views/${viewId}/use`, {
    method: "POST",
  });
}

export async function fetchIntelFileDetail(intelFileId: string) {
  return request<IntelFileDetailData>(`/api/v1/intel-files/${intelFileId}`);
}

export async function overrideIntelFileStatus(intelFileId: string, body: StatusOverrideRequest) {
  return request<StatusOverrideData>(`/api/v1/intel-files/${intelFileId}/status`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function updateIntelFileCollaboration(
  intelFileId: string,
  body: CollaborationUpdateRequest,
) {
  return request<CollaborationData>(`/api/v1/intel-files/${intelFileId}/collaboration`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function fetchIntelFileComments(intelFileId: string) {
  return request<CommentListData>(`/api/v1/intel-files/${intelFileId}/comments`);
}

export async function createIntelFileComment(intelFileId: string, body: string) {
  return request<CommentCreateData>(`/api/v1/intel-files/${intelFileId}/comments`, {
    method: "POST",
    body: JSON.stringify({ body }),
  });
}

export async function attachEvidence(intelFileId: string, body: EvidenceAttachRequest) {
  return request<EvidenceAttachData>(`/api/v1/intel-files/${intelFileId}/evidence`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function fetchMatchSuggestions(intelFileId: string, status = "open") {
  const params = new URLSearchParams({ status });
  return request<MatchSuggestionListData>(
    `/api/v1/intel-files/${intelFileId}/match-suggestions?${params.toString()}`,
  );
}

export async function fetchTrackingQueries(intelFileId: string) {
  return request<TrackingQueryListData>(`/api/v1/intel-files/${intelFileId}/tracking-queries`);
}

export async function generateTrackingQueries(intelFileId: string, limit = 12, regenerate = false) {
  return request<TrackingQueryGenerateData>(`/api/v1/intel-files/${intelFileId}/tracking-queries`, {
    method: "POST",
    body: JSON.stringify({ limit, regenerate }),
  });
}

export async function updateTrackingQueryEnabled(
  intelFileId: string,
  trackingQueryId: string,
  enabled: boolean,
) {
  return request<TrackingQueryUpdateData>(
    `/api/v1/intel-files/${intelFileId}/tracking-queries/${trackingQueryId}`,
    {
      method: "PATCH",
      body: JSON.stringify({ enabled }),
    },
  );
}

export async function acceptMatchSuggestion(suggestionId: string, rationale?: string) {
  return request<MatchSuggestionAcceptData>(`/api/v1/match-suggestions/${suggestionId}/accept`, {
    method: "POST",
    body: JSON.stringify({ rationale: rationale ?? null }),
  });
}

export async function updateMatchSuggestionStatus(suggestionId: string, status: "open" | "dismissed") {
  return request<MatchSuggestionStatusUpdateData>(`/api/v1/match-suggestions/${suggestionId}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export async function generateSourceCheckMatchSuggestions(runId: string, minConfidence = 0.65) {
  return request<MatchSuggestionGenerateData>(`/api/v1/source-checks/runs/${runId}/match-suggestions`, {
    method: "POST",
    body: JSON.stringify({ min_confidence: minConfidence }),
  });
}

export async function fetchAlerts(status?: AlertStatusFilter, severity?: AlertSeverityFilter) {
  const params = new URLSearchParams();
  if (status && status !== "all") {
    params.set("status", status);
  }
  if (severity && severity !== "all") {
    params.set("severity", severity);
  }
  const query = params.toString();
  return request<AlertListData>(`/api/v1/alerts${query ? `?${query}` : ""}`);
}

export async function updateAlertStatus(alertId: string, body: AlertUpdateRequest) {
  return request<AlertSummary>(`/api/v1/alerts/${alertId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function fetchDailyBriefing(hours = 24) {
  const params = new URLSearchParams({ hours: String(hours) });
  return request<DailyBriefingData>(`/api/v1/briefings/daily?${params.toString()}`);
}

export async function fetchWeeklyRetrospective(days = 7) {
  const params = new URLSearchParams({ days: String(days) });
  return request<WeeklyRetrospectiveData>(`/api/v1/briefings/weekly?${params.toString()}`);
}

export async function bootstrapWorkspace(body: BootstrapRequest) {
  return request<BootstrapData>("/api/v1/auth/bootstrap", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function fetchWorkspaces() {
  return request<WorkspaceListData>("/api/v1/workspaces");
}

export async function fetchWorkspaceMembers(workspaceId: string) {
  return request<WorkspaceMemberListData>(`/api/v1/workspaces/${workspaceId}/members`);
}

export async function addWorkspaceMember(workspaceId: string, body: WorkspaceMemberCreateRequest) {
  return request<WorkspaceMemberCreateData>(`/api/v1/workspaces/${workspaceId}/members`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function fetchWorkspaceAuditEvents(workspaceId: string) {
  return request<AuditEventListData>(`/api/v1/workspaces/${workspaceId}/audit-events`);
}

export async function fetchWorkspaceAuditCsv(workspaceId: string) {
  const response = await fetch(`${API_BASE}/api/v1/workspaces/${workspaceId}/audit-events.csv`, {
    headers: workspaceHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Audit export failed: ${response.status}`);
  }
  return response.blob();
}

export async function fetchSourceCheckRuns(limit = 10) {
  const params = new URLSearchParams({ limit: String(limit) });
  return request<SourceCheckRunListData>(`/api/v1/source-checks/runs?${params.toString()}`);
}

export async function fetchSourceProviderHealth(limit = 25) {
  const params = new URLSearchParams({ limit: String(limit) });
  return request<SourceProviderHealthData>(`/api/v1/source-checks/provider-health?${params.toString()}`);
}

export async function runSourceChecks(limit = 20) {
  return request<SourceCheckRunData>("/api/v1/source-checks/run", {
    method: "POST",
    body: JSON.stringify({ limit }),
  });
}
