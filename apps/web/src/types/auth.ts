export type UserRead = {
  id: string;
  email: string;
  name: string;
  created_at: string;
};

export type WorkspaceRead = {
  id: string;
  name: string;
  slug: string;
  created_at: string;
};

export type WorkspaceMembershipRead = {
  id: string;
  workspace_id: string;
  user_id: string;
  role: string;
  created_at: string;
};

export type WorkspaceMemberRead = {
  membership_id: string;
  user_id: string;
  email: string;
  name: string;
  role: "admin" | "member";
  joined_at: string;
};

export type AuditEventRead = {
  id: string;
  workspace_id: string | null;
  actor_email: string | null;
  action: string;
  target_type: string | null;
  target_id: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
};

export type BootstrapRequest = {
  email: string;
  name: string;
  workspace_name: string;
};

export type WorkspaceMemberCreateRequest = {
  email: string;
  name: string;
  role: "admin" | "member";
};

export type BootstrapData = {
  user: UserRead;
  workspace: WorkspaceRead;
  membership: WorkspaceMembershipRead;
  access_token: string;
};

export type WorkspaceListData = {
  items: WorkspaceRead[];
  total: number;
};

export type WorkspaceMemberListData = {
  items: WorkspaceMemberRead[];
  total: number;
};

export type WorkspaceMemberCreateData = {
  member: WorkspaceMemberRead;
  access_token: string;
};

export type AuditEventListData = {
  items: AuditEventRead[];
  total: number;
};
