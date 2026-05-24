"use client";

import { useEffect, useState } from "react";

import {
  addWorkspaceMember,
  bootstrapWorkspace,
  fetchWorkspaceAuditCsv,
  fetchWorkspaceAuditEvents,
  fetchWorkspaceMembers,
  fetchWorkspaces,
} from "@/lib/api";
import type { AuditEventRead, WorkspaceMemberRead, WorkspaceRead } from "@/types/auth";

export default function WorkspacePage() {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [workspaceName, setWorkspaceName] = useState("");
  const [items, setItems] = useState<WorkspaceRead[]>([]);
  const [members, setMembers] = useState<WorkspaceMemberRead[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEventRead[]>([]);
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(null);
  const [memberEmail, setMemberEmail] = useState("");
  const [memberName, setMemberName] = useState("");
  const [memberRole, setMemberRole] = useState<"admin" | "member">("member");
  const [issuedToken, setIssuedToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [addingMember, setAddingMember] = useState(false);
  const [exportingAudit, setExportingAudit] = useState(false);

  async function loadWorkspaces() {
    setError(null);
    try {
      const result = await fetchWorkspaces();
      if (!result.success || !result.data) {
        setError(result.error?.message ?? "Failed to load workspaces.");
        return;
      }
      setItems(result.data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load workspaces.");
    }
  }

  async function loadMembers(workspaceId: string) {
    setError(null);
    try {
      const result = await fetchWorkspaceMembers(workspaceId);
      if (!result.success || !result.data) {
        setError(result.error?.message ?? "Failed to load members.");
        return;
      }
      setMembers(result.data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load members.");
    }
  }

  async function loadAuditEvents(workspaceId: string) {
    try {
      const result = await fetchWorkspaceAuditEvents(workspaceId);
      if (result.success && result.data) {
        setAuditEvents(result.data.items);
      }
    } catch {
      setAuditEvents([]);
    }
  }

  useEffect(() => {
    const workspaceId = window.localStorage.getItem("signal-tracker:workspace-id");
    setActiveWorkspaceId(workspaceId);
    setEmail(window.localStorage.getItem("signal-tracker:user-email") ?? "");
    void loadWorkspaces();
    if (workspaceId) {
      void loadMembers(workspaceId);
      void loadAuditEvents(workspaceId);
    }
  }, []);

  async function handleBootstrap(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const result = await bootstrapWorkspace({
        email: email.trim(),
        name: name.trim(),
        workspace_name: workspaceName.trim(),
      });
      if (!result.success || !result.data) {
        setError(result.error?.message ?? "Failed to create workspace.");
        return;
      }
      window.localStorage.setItem("signal-tracker:user-email", result.data.user.email);
      window.localStorage.setItem("signal-tracker:user-token", result.data.access_token);
      window.localStorage.setItem("signal-tracker:workspace-id", result.data.workspace.id);
      setActiveWorkspaceId(result.data.workspace.id);
      setEmail(result.data.user.email);
      setWorkspaceName("");
      setIssuedToken(result.data.access_token);
      await loadWorkspaces();
      await loadMembers(result.data.workspace.id);
      await loadAuditEvents(result.data.workspace.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create workspace.");
    } finally {
      setSaving(false);
    }
  }

  function selectWorkspace(workspace: WorkspaceRead) {
    window.localStorage.setItem("signal-tracker:workspace-id", workspace.id);
    setActiveWorkspaceId(workspace.id);
    void loadMembers(workspace.id);
    void loadAuditEvents(workspace.id);
  }

  async function handleAddMember(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!activeWorkspaceId) {
      setError("Select a workspace first.");
      return;
    }
    setAddingMember(true);
    setError(null);
    try {
      const result = await addWorkspaceMember(activeWorkspaceId, {
        email: memberEmail.trim(),
        name: memberName.trim(),
        role: memberRole,
      });
      if (!result.success || !result.data) {
        setError(result.error?.message ?? "Failed to add member.");
        return;
      }
      setMemberEmail("");
      setMemberName("");
      setMemberRole("member");
      setIssuedToken(result.data.access_token);
      await loadMembers(activeWorkspaceId);
      await loadAuditEvents(activeWorkspaceId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add member.");
    } finally {
      setAddingMember(false);
    }
  }

  async function handleExportAudit() {
    if (!activeWorkspaceId) {
      return;
    }
    setExportingAudit(true);
    setError(null);
    try {
      const blob = await fetchWorkspaceAuditCsv(activeWorkspaceId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `workspace-${activeWorkspaceId}-audit-events.csv`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to export audit events.");
    } finally {
      setExportingAudit(false);
    }
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Workspace</h1>
        <p className="mt-2 text-slate-400">Local workspace context for commercial workflows.</p>
      </div>

      <form onSubmit={(event) => void handleBootstrap(event)} className="rounded-lg border border-slate-800 p-4">
        <div className="grid gap-4 md:grid-cols-3">
          <label className="block text-sm">
            <span className="text-slate-400">Email</span>
            <input value={email} onChange={(event) => setEmail(event.target.value)} className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm" />
          </label>
          <label className="block text-sm">
            <span className="text-slate-400">Name</span>
            <input value={name} onChange={(event) => setName(event.target.value)} className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm" />
          </label>
          <label className="block text-sm">
            <span className="text-slate-400">Workspace name</span>
            <input value={workspaceName} onChange={(event) => setWorkspaceName(event.target.value)} className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm" />
          </label>
        </div>
        {error ? <p className="mt-3 text-sm text-red-400">{error}</p> : null}
        {issuedToken ? (
          <div className="mt-3 rounded border border-amber-700/50 bg-amber-950/30 p-3 text-xs text-amber-100">
            <p className="font-medium">Access token</p>
            <p className="mt-1 break-all font-mono">{issuedToken}</p>
          </div>
        ) : null}
        <button type="submit" disabled={saving} className="mt-4 rounded border border-slate-700 px-3 py-2 text-sm text-sky-300 hover:bg-slate-800 disabled:opacity-50">
          {saving ? "Saving..." : "Create and select workspace"}
        </button>
      </form>

      <div>
        <h2 className="text-lg font-medium">Available workspaces</h2>
        {items.length === 0 ? (
          <p className="mt-2 text-sm text-slate-400">No workspaces for the current email yet.</p>
        ) : (
          <ul className="mt-3 space-y-2">
            {items.map((workspace) => (
              <li key={workspace.id} className="flex items-center justify-between rounded border border-slate-800 px-4 py-3 text-sm">
                <div>
                  <p className="font-medium text-slate-200">{workspace.name}</p>
                  <p className="text-xs text-slate-500">{workspace.slug}</p>
                </div>
                <button type="button" onClick={() => selectWorkspace(workspace)} className="text-sky-300 hover:text-sky-200">
                  {activeWorkspaceId === workspace.id ? "Selected" : "Select"}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_360px]">
        <div>
          <h2 className="text-lg font-medium">Members</h2>
          {members.length === 0 ? (
            <p className="mt-2 text-sm text-slate-400">No members loaded for the selected workspace.</p>
          ) : (
            <ul className="mt-3 divide-y divide-slate-800 rounded border border-slate-800">
              {members.map((member) => (
                <li key={member.membership_id} className="flex items-center justify-between px-4 py-3 text-sm">
                  <div>
                    <p className="font-medium text-slate-200">{member.name}</p>
                    <p className="text-xs text-slate-500">{member.email}</p>
                  </div>
                  <span className="rounded border border-slate-700 px-2 py-1 text-xs text-slate-300">{member.role}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <form onSubmit={(event) => void handleAddMember(event)} className="rounded-lg border border-slate-800 p-4">
          <h2 className="text-lg font-medium">Add member</h2>
          <label className="mt-4 block text-sm">
            <span className="text-slate-400">Email</span>
            <input value={memberEmail} onChange={(event) => setMemberEmail(event.target.value)} className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm" />
          </label>
          <label className="mt-3 block text-sm">
            <span className="text-slate-400">Name</span>
            <input value={memberName} onChange={(event) => setMemberName(event.target.value)} className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm" />
          </label>
          <label className="mt-3 block text-sm">
            <span className="text-slate-400">Role</span>
            <select value={memberRole} onChange={(event) => setMemberRole(event.target.value as "admin" | "member")} className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2 text-sm">
              <option value="member">member</option>
              <option value="admin">admin</option>
            </select>
          </label>
          <button type="submit" disabled={addingMember || !activeWorkspaceId} className="mt-4 rounded border border-slate-700 px-3 py-2 text-sm text-sky-300 hover:bg-slate-800 disabled:opacity-50">
            {addingMember ? "Adding..." : "Add member"}
          </button>
        </form>
      </div>

      <div>
        <h2 className="text-lg font-medium">Audit events</h2>
        {auditEvents.length === 0 ? (
          <p className="mt-2 text-sm text-slate-400">No audit events loaded for the selected workspace.</p>
        ) : (
          <>
            {activeWorkspaceId ? (
              <button
                type="button"
                onClick={() => void handleExportAudit()}
                disabled={exportingAudit}
                className="mt-3 inline-block rounded border border-slate-700 px-3 py-2 text-sm text-sky-300 hover:bg-slate-800"
              >
                {exportingAudit ? "Exporting..." : "Export CSV"}
              </button>
            ) : null}
            <ul className="mt-3 divide-y divide-slate-800 rounded border border-slate-800">
              {auditEvents.map((event) => (
                <li key={event.id} className="px-4 py-3 text-sm">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium text-slate-200">{event.action}</p>
                    <span className="text-xs text-slate-500">{new Date(event.created_at).toLocaleString()}</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">{event.actor_email ?? "system"}</p>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </section>
  );
}
