// Chatita Mail v3.0 - API client
import axios from "axios";
import type { EmailCategory, EmailDetail, EmailListItem, EmailStatus } from "../types";

const api = axios.create({
  baseURL: "/api",
  timeout: 30000,
});

export async function listEmails(params: {
  status?: EmailStatus;
  category?: EmailCategory;
  limit?: number;
}): Promise<EmailListItem[]> {
  const { data } = await api.get<EmailListItem[]>("/inbox/emails", { params });
  return data;
}

export async function getEmail(id: string): Promise<EmailDetail> {
  const { data } = await api.get<EmailDetail>(`/inbox/emails/${id}`);
  return data;
}

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

export default api;
