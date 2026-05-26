import type { Applicant, ApplicationItem, DashboardData, DiscoveryResult, DocumentItem, PendingAction, PortalSession, ProfileAnalysis, Program, ProgramMatch, SourceBrief, UniversityBrief, UrlValidationResult } from "./types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

type ProgramFilters = {
  search?: string;
  country?: string;
  field?: string;
  university?: string;
  review_status?: string;
  min_confidence?: number | string;
  limit?: number;
  offset?: number;
};

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    ...init,
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const detail = data?.detail || data?.message || res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data as T;
}

function queryString(params: Record<string, unknown>) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  });
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export async function getDefaultApplicant(): Promise<Applicant> {
  return apiFetch<Applicant>("/applicants/default");
}

export async function getApplicant(id: number): Promise<Applicant> {
  return apiFetch<Applicant>(`/applicants/${id}`);
}

export async function updateApplicant(id: number, data: Partial<Applicant>): Promise<Applicant> {
  return apiFetch<Applicant>(`/applicants/${id}`, { method: "PUT", body: JSON.stringify(data) });
}

export async function analyzeApplicant(id: number): Promise<ProfileAnalysis> {
  return apiFetch<ProfileAnalysis>(`/applicants/${id}/analyze`, { method: "POST", body: JSON.stringify({}) });
}

export async function getDashboard(applicantId: number): Promise<DashboardData> {
  return apiFetch<DashboardData>(`/dashboard/${applicantId}`);
}

export async function getPrograms(filters: ProgramFilters = {}): Promise<Program[]> {
  const data = await apiFetch<{ total: number; items: Program[] }>(`/programs${queryString({ limit: 50, ...filters })}`);
  return data.items;
}

export async function getProgram(id: string | number): Promise<Program> {
  return apiFetch<Program>(`/programs/${id}`);
}

export async function generateMatches(applicantId: number): Promise<{ status: string; total: number; items: ProgramMatch[] }> {
  return apiFetch(`/matches/generate/${applicantId}`, { method: "POST", body: JSON.stringify({}) });
}

export async function getMatches(applicantId: number): Promise<ProgramMatch[]> {
  return apiFetch<ProgramMatch[]>(`/matches/${applicantId}`);
}

export async function addApplication(applicantId: number, programId: number): Promise<ApplicationItem> {
  return apiFetch<ApplicationItem>("/applications", { method: "POST", body: JSON.stringify({ applicant_id: applicantId, program_id: programId }) });
}

export async function getApplications(applicantId: number): Promise<ApplicationItem[]> {
  return apiFetch<ApplicationItem[]>(`/applications${queryString({ applicant_id: applicantId })}`);
}

export async function updateApplicationStatus(applicationId: number, status: string): Promise<ApplicationItem> {
  return apiFetch<ApplicationItem>(`/applications/${applicationId}/status`, { method: "PUT", body: JSON.stringify({ status }) });
}

export async function updateApplication(applicationId: number, data: Partial<ApplicationItem>): Promise<ApplicationItem> {
  return apiFetch<ApplicationItem>(`/applications/${applicationId}`, { method: "PUT", body: JSON.stringify(data) });
}

export async function getDocuments(applicantId: number): Promise<DocumentItem[]> {
  return apiFetch<DocumentItem[]>(`/documents${queryString({ applicant_id: applicantId })}`);
}

export async function uploadDocument(applicantId: number, documentType: string, file: File, notes?: string): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append("applicant_id", String(applicantId));
  formData.append("document_type", documentType);
  if (notes) formData.append("notes", notes);
  formData.append("file", file);
  const res = await fetch(`${API}/documents/upload`, { method: "POST", body: formData });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const detail = data?.detail || data?.message || res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data as DocumentItem;
}

export function downloadDocument(documentId: number): string {
  return `${API}/documents/${documentId}/download`;
}

export async function createDocument(data: Partial<DocumentItem>): Promise<DocumentItem> {
  return apiFetch<DocumentItem>("/documents", { method: "POST", body: JSON.stringify(data) });
}

export async function updateDocument(documentId: number, data: Partial<DocumentItem>): Promise<DocumentItem> {
  return apiFetch<DocumentItem>(`/documents/${documentId}`, { method: "PUT", body: JSON.stringify(data) });
}

export async function updateDocumentStatus(documentId: number, status: string): Promise<DocumentItem> {
  return apiFetch<DocumentItem>(`/documents/${documentId}/status`, { method: "PUT", body: JSON.stringify({ status }) });
}

export async function deleteDocument(documentId: number): Promise<DocumentItem> {
  return apiFetch<DocumentItem>(`/documents/${documentId}`, { method: "DELETE" });
}

export async function generateDocumentChecklist(applicantId: number, programId: number): Promise<unknown> {
  return apiFetch(`/documents/checklist/${programId}`, { method: "POST", body: JSON.stringify({ applicant_id: applicantId }) });
}

export const generateChecklist = generateDocumentChecklist;

export async function startBrowserTask(applicantId: number, programId: number, executorType: string): Promise<unknown> {
  return apiFetch("/browser-agent/start-task", { method: "POST", body: JSON.stringify({ applicant_id: applicantId, program_id: programId, executor_type: executorType }) });
}

export async function runBrowserTaskNextStep(taskId: number): Promise<unknown> {
  return apiFetch("/browser-agent/run-next-step", { method: "POST", body: JSON.stringify({ task_id: taskId }) });
}

export async function approveBrowserAction(taskId: number, actionId = "next"): Promise<unknown> {
  return apiFetch("/browser-agent/approve-action", { method: "POST", body: JSON.stringify({ task_id: taskId, action_id: actionId }) });
}

export async function stopBrowserTask(taskId: number): Promise<unknown> {
  return apiFetch("/browser-agent/stop-task", { method: "POST", body: JSON.stringify({ task_id: taskId }) });
}

export async function getBrowserLogs(taskId: number): Promise<unknown> {
  return apiFetch(`/browser-agent/logs${queryString({ task_id: taskId })}`);
}

export async function getBrowserExecutors(): Promise<unknown> {
  return apiFetch("/browser-agent/executors");
}

export async function getOpenCliStatus(): Promise<unknown> {
  return apiFetch("/browser-agent/opencli/status");
}

export async function getEmails(applicantId: number): Promise<unknown[]> {
  return apiFetch<unknown[]>(`/emails${queryString({ applicant_id: applicantId })}`);
}

export async function generateRecommendations(applicantId: number, provider = "mock"): Promise<unknown> {
  return apiFetch(`/recommendations/generate/${applicantId}${queryString({ provider })}`, { method: "POST", body: JSON.stringify({}) });
}

export async function getRecommendations(applicantId: number): Promise<unknown> {
  return apiFetch(`/recommendations/${applicantId}`);
}

export async function startPortalSession(applicantId: number, programId: number | null, executorType: string, portalUrl: string, snapshotText?: string): Promise<PortalSession> {
  return apiFetch<PortalSession>("/portal-assistant/start", {
    method: "POST",
    body: JSON.stringify({ applicant_id: applicantId, program_id: programId, executor_type: executorType, portal_url: portalUrl, snapshot_text: snapshotText }),
  });
}

export async function confirmPortalLoggedIn(sessionId: number, snapshotText?: string): Promise<PortalSession> {
  return apiFetch<PortalSession>("/portal-assistant/user-logged-in", { method: "POST", body: JSON.stringify({ session_id: sessionId, snapshot_text: snapshotText }) });
}

export async function generatePortalFillPlan(sessionId: number, snapshotText?: string): Promise<{ session: PortalSession; items: PendingAction[] }> {
  return apiFetch<{ session: PortalSession; items: PendingAction[] }>("/portal-assistant/generate-fill-plan", { method: "POST", body: JSON.stringify({ session_id: sessionId, snapshot_text: snapshotText }) });
}

export async function runPortalFillStep(sessionId: number): Promise<unknown> {
  return apiFetch("/portal-assistant/run-fill-step", { method: "POST", body: JSON.stringify({ session_id: sessionId }) });
}

export async function stopPortalSession(sessionId: number): Promise<PortalSession> {
  return apiFetch<PortalSession>("/portal-assistant/stop", { method: "POST", body: JSON.stringify({ session_id: sessionId }) });
}

export async function getPortalSession(sessionId: number): Promise<PortalSession> {
  return apiFetch<PortalSession>(`/portal-assistant/sessions/${sessionId}`);
}

export async function getPortalLogs(sessionId: number): Promise<unknown> {
  return apiFetch(`/portal-assistant/logs${queryString({ session_id: sessionId })}`);
}

export async function getPendingActions(sessionId: number): Promise<{ session_id: number; items: PendingAction[] }> {
  return apiFetch<{ session_id: number; items: PendingAction[] }>(`/portal-assistant/pending-actions${queryString({ session_id: sessionId })}`);
}

export async function approvePendingAction(actionId: number): Promise<PendingAction> {
  return apiFetch<PendingAction>(`/portal-assistant/actions/${actionId}/approve`, { method: "POST", body: JSON.stringify({}) });
}

export async function rejectPendingAction(actionId: number): Promise<PendingAction> {
  return apiFetch<PendingAction>(`/portal-assistant/actions/${actionId}/reject`, { method: "POST", body: JSON.stringify({}) });
}

export async function markPendingActionUserCompleted(actionId: number): Promise<PendingAction> {
  return apiFetch<PendingAction>(`/portal-assistant/actions/${actionId}/mark-user-completed`, { method: "POST", body: JSON.stringify({}) });
}

export async function executePendingAction(actionId: number): Promise<unknown> {
  return apiFetch(`/portal-assistant/actions/${actionId}/execute`, { method: "POST", body: JSON.stringify({}) });
}

export async function getDiscoveryRegions(): Promise<string[]> {
  return apiFetch<string[]>("/discovery/regions");
}

export async function getDiscoveryUniversities(region: string): Promise<UniversityBrief[]> {
  return apiFetch<UniversityBrief[]>(`/discovery/universities?region=${encodeURIComponent(region)}`);
}

export async function getDiscoverySources(universityId: number): Promise<SourceBrief[]> {
  return apiFetch<SourceBrief[]>(`/discovery/sources?university_id=${universityId}`);
}

export async function getDiscoveryFields(): Promise<string[]> {
  return apiFetch<string[]>("/discovery/fields");
}

export async function findPrograms(payload: {
  university_id?: number;
  field?: string;
  url?: string;
  engine?: string;
  max_pages?: number;
}): Promise<DiscoveryResult> {
  return apiFetch<DiscoveryResult>("/discovery/find-programs", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function analyzeDiscoveryUrl(url: string): Promise<UrlValidationResult> {
  return apiFetch<UrlValidationResult>("/discovery/analyze-url", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

export async function getDiscoveryResults(runId: number): Promise<DiscoveryResult> {
  return apiFetch<DiscoveryResult>(`/discovery/results/${runId}`);
}
