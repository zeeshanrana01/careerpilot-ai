const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function fetchProfile() {
  const res = await fetch(`${BASE_URL}/api/profile`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch profile");
  return res.json();
}

export async function fetchMatches() {
  const res = await fetch(`${BASE_URL}/api/matches`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch matches");
  return res.json();
}

export async function fetchJobs() {
  const res = await fetch(`${BASE_URL}/api/jobs`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch jobs");
  return res.json();
}

export async function ingestJob(payload: any) {
  const res = await fetch(`${BASE_URL}/api/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function draftApplication(jobId: string) {
  const res = await fetch(`${BASE_URL}/api/applications/draft/${jobId}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to draft application");
  return res.json();
}

export async function fetchApplication(jobId: string) {
  const res = await fetch(`${BASE_URL}/api/applications/${jobId}`, { cache: "no-store" });
  if (!res.ok) return null;
  return res.json();
}

export async function approveApplication(appId: string) {
  const res = await fetch(`${BASE_URL}/api/applications/${appId}/approve`, {
    method: "POST",
  });
  return res.json();
}

export async function rejectApplication(appId: string) {
  const res = await fetch(`${BASE_URL}/api/applications/${appId}/reject`, {
    method: "POST",
  });
  return res.json();
}

export async function fetchAudit() {
  const res = await fetch(`${BASE_URL}/api/audit`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch audit events");
  return res.json();
}
