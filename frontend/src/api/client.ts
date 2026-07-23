// Chatita Mail v3.0 - API client
import axios from "axios";
import type {
  Commitment,
  EmailCategory,
  EmailDetail,
  EmailListItem,
  EmailStatus,
  InboxStats,
  SyncResult,
  Task,
} from "../types";

const api = axios.create({
  baseURL: "/api",
  timeout: 60000,
});

// ── Inbox ──────────────────────────────────────────────────
export async function listEmails(params: {
  status?: EmailStatus;
  category?: EmailCategory;
  unread_only?: boolean;
  search?: string;
  limit?: number;
}): Promise<EmailListItem[]> {
  const { data } = await api.get<EmailListItem[]>("/inbox/emails", { params });
  return data;
}

export async function getEmail(id: string): Promise<EmailDetail> {
  const { data } = await api.get<EmailDetail>(`/inbox/emails/${id}`);
  return data;
}

export async function getStats(): Promise<InboxStats> {
  const { data } = await api.get<InboxStats>("/inbox/stats");
  return data;
}

export async function syncGmail(
  maxResults = 30,
  triage = true
): Promise<SyncResult> {
  const { data } = await api.post<SyncResult>("/inbox/sync/gmail", null, {
    params: { max_results: maxResults, triage },
  });
  return data;
}

export async function gmailHealth(): Promise<Record<string, unknown>> {
  const { data } = await api.get("/inbox/gmail/health");
  return data;
}

// ── Actions ────────────────────────────────────────────────
export async function setStatus(
  id: string,
  status: EmailStatus
): Promise<EmailListItem> {
  const { data } = await api.patch<EmailListItem>(`/inbox/emails/${id}/status`, {
    status,
  });
  return data;
}

export async function setRead(id: string, is_read: boolean): Promise<EmailListItem> {
  const { data } = await api.patch<EmailListItem>(`/inbox/emails/${id}/read`, {
    is_read,
  });
  return data;
}

export async function unsubscribeEmail(id: string): Promise<Record<string, unknown>> {
  const { data } = await api.post(`/inbox/emails/${id}/unsubscribe`);
  return data;
}

// ── Classification / security ──────────────────────────────
export async function triageEmail(id: string): Promise<unknown> {
  const { data } = await api.post(`/classify/${id}`);
  return data;
}

export async function reclassify(id: string, category: EmailCategory): Promise<unknown> {
  const { data } = await api.patch(`/classify/${id}/reclassify`, { category });
  return data;
}

export async function releaseFromQuarantine(id: string): Promise<unknown> {
  const { data } = await api.post(`/security/${id}/release`);
  return data;
}

// ── Phase 2: Tasks & Commitments ───────────────────────────
export async function listTasks(status = "pending"): Promise<Task[]> {
  const { data } = await api.get<Task[]>("/tasks", { params: { status } });
  return data;
}

export async function listCommitments(status = "pending"): Promise<Commitment[]> {
  const { data } = await api.get<Commitment[]>("/commitments", { params: { status } });
  return data;
}

export async function extractTasks(id: string): Promise<{
  source: string;
  tasks_extracted: number;
  commitments_extracted: number;
}> {
  const { data } = await api.post(`/inbox/emails/${id}/extract`);
  return data;
}

export async function updateTask(id: string, status: string): Promise<Task> {
  const { data } = await api.patch<Task>(`/tasks/${id}`, { status });
  return data;
}

// ── Phase 2: Composer (summaries + reply drafts) ───────────
export interface EmailSummary {
  tldr: string;
  key_points: string[];
  suggested_action: string;
  requires_reply: boolean;
  source: string;
}

export interface ReplyDraft {
  subject: string;
  body: string;
  tone: string;
  source: string;
}

export async function summarizeEmail(id: string): Promise<EmailSummary> {
  const { data } = await api.post<EmailSummary>(`/inbox/emails/${id}/summarize`);
  return data;
}

export async function draftReply(
  id: string,
  tone = "professional",
  instructions?: string
): Promise<ReplyDraft> {
  const { data } = await api.post<ReplyDraft>(`/inbox/emails/${id}/draft-reply`, {
    tone,
    instructions,
  });
  return data;
}

export default api;
