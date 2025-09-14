
export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8080';

async function req(path: string, init?: RequestInit) {
  const r = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    ...init,
  });
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.headers.get('content-type')?.includes('application/json') ? r.json() : r.text();
}

export const api = {
  health: () => req('/healthz'),
  plans: () => req('/plans'),
  createUser: (email: string) => req('/users', { method: 'POST', body: JSON.stringify({ email }) }),
  subscribe: (user_id: string, plan_code: string) => req('/subscriptions', { method: 'POST', body: JSON.stringify({ user_id, plan_code }) }),
  addUsage: (user_id: string, metric: string, quantity: number) =>
    req('/usage', { method: 'POST', body: JSON.stringify({ user_id, metric, quantity }) }),
  generateInvoice: (user_id: string) => req(`/invoices/generate/${user_id}`, { method: 'POST' }),
};

export const invoicesByUser = (user_id: string) => req(`/invoices/${user_id}`);
export const paymentsByUser = (user_id: string) => req(`/payments/${user_id}`);
