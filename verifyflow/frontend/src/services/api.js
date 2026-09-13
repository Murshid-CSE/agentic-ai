/**
 * API client for VerifyFlow backend.
 * Provides fallback mock data if backend server is temporarily unreachable.
 */

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const FALLBACK_DEMO_CASES = [
  {
    request_id: "VF-CASE-A",
    label: "Routine Safe Invoice",
    badge: "Instant AI Approval",
    scenarioType: "safe",
    description: "Known vendor, matching domain and registered bank account. Zero anomalies.",
    expected_action: "APPROVE",
    expected_score: 0,
    expected_level: "LOW",
    vendor_name: "Acme Supplies",
    sender_email: "accounts@acme.in",
    sender_domain: "acme.in",
    invoice_number: "INV-1001",
    amount: 42000,
    requested_account: "BANK-ACME-001",
    urgency: "normal",
  },
  {
    request_id: "VF-CASE-B",
    label: "The BEC Cyberattack",
    badge: "High Risk Attack Blocked",
    scenarioType: "attack",
    description: "Lookalike domain (acme-payments.co) + unverified bank account swap ($125,000 wire).",
    expected_action: "HUMAN_REVIEW",
    expected_score: 100,
    expected_level: "CRITICAL",
    vendor_name: "Acme Supplies",
    sender_email: "billing@acme-payments.co",
    sender_domain: "acme-payments.co",
    invoice_number: "INV-4938",
    amount: 125000,
    requested_account: "BANK-ACME-999",
    urgency: "urgent",
  },
  {
    request_id: "VF-CASE-C",
    label: "Outage & Self-Healing AI",
    badge: "Autonomous Adaptation",
    scenarioType: "recovery",
    description: "Bank change requested while primary verification API is down. Agent pivots to secondary phone check.",
    expected_action: "HUMAN_REVIEW",
    expected_score: 60,
    expected_level: "HIGH",
    vendor_name: "Delta Components",
    sender_email: "finance@delta-corp.com",
    sender_domain: "delta-corp.com",
    invoice_number: "INV-7721",
    amount: 45000,
    requested_account: "BANK-DELTA-NEW-099",
    urgency: "normal",
  },
];

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(1500) });
    return res.ok;
  } catch {
    return false;
  }
}

export async function fetchDemoCases() {
  try {
    const res = await fetch(`${API_BASE}/demo-cases`, { signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) return data;
    }
  } catch {
    // Fall back to built-in presets
  }
  return FALLBACK_DEMO_CASES;
}

export async function fetchRecentCases() {
  try {
    const res = await fetch(`${API_BASE}/cases?limit=25`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Could not fetch recent cases from backend:", err);
  }
  return [];
}

export async function runInvestigation(paymentRequest, options = {}) {
  const params = new URLSearchParams();
  if (options.verification_available !== undefined) {
    params.set("verification_available", String(options.verification_available));
  }
  if (options.verification_verified !== undefined && options.verification_verified !== null) {
    params.set("verification_verified", String(options.verification_verified));
  }
  if (options.enable_secondary_verification !== undefined) {
    params.set("enable_secondary_verification", String(options.enable_secondary_verification));
  }
  if (options.trusted_contact_reachable !== undefined) {
    params.set("trusted_contact_reachable", String(options.trusted_contact_reachable));
  }
  if (options.trusted_contact_confirmed !== undefined && options.trusted_contact_confirmed !== null) {
    params.set("trusted_contact_confirmed", String(options.trusted_contact_confirmed));
  }

  const queryStr = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${API_BASE}/investigate${queryStr}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(paymentRequest),
  });
  if (!res.ok) {
    throw new Error(`Investigation failed with status ${res.status}`);
  }
  return await res.json();
}

export async function runRawInvestigation(rawPayload, options = {}) {
  const params = new URLSearchParams();
  if (options.enable_secondary_verification !== undefined) {
    params.set("enable_secondary_verification", String(options.enable_secondary_verification));
  }
  if (options.trusted_contact_reachable !== undefined) {
    params.set("trusted_contact_reachable", String(options.trusted_contact_reachable));
  }
  if (options.trusted_contact_confirmed !== undefined && options.trusted_contact_confirmed !== null) {
    params.set("trusted_contact_confirmed", String(options.trusted_contact_confirmed));
  }

  const queryStr = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`${API_BASE}/investigate/raw${queryStr}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(rawPayload),
  });
  if (!res.ok) {
    throw new Error(`Raw text investigation failed with status ${res.status}`);
  }
  return await res.json();
}

export async function fetchCaseTrace(caseId) {
  const res = await fetch(`${API_BASE}/cases/${encodeURIComponent(caseId)}/trace`);
  if (!res.ok) throw new Error("Could not fetch trace");
  return await res.json();
}

export async function fetchCaseEvidence(caseId) {
  const res = await fetch(`${API_BASE}/cases/${encodeURIComponent(caseId)}/evidence`);
  if (!res.ok) throw new Error("Could not fetch evidence");
  return await res.json();
}

export async function fetchBenchmarkCases() {
  try {
    const res = await fetch(`${API_BASE}/evaluation/cases`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Could not fetch benchmark cases from API:", err);
  }
  return [];
}

export async function fetchBenchmarkResults() {
  try {
    const res = await fetch(`${API_BASE}/evaluation/benchmark`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn("Could not fetch benchmark results from API:", err);
  }
  return null;
}

export async function runBenchmark() {
  const res = await fetch(`${API_BASE}/evaluation/run`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Benchmark execution failed with status ${res.status}`);
  return await res.json();
}
