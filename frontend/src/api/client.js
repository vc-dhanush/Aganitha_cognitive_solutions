const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true';

function buildUrl(path) {
  if (path.startsWith('http')) return path;
  if (API_URL) return `${API_URL}${path}`;
  return path;
}

async function request(path, options = {}) {
  const url = buildUrl(path);
  const response = await fetch(url, options);
  if (!response.ok) {
    let detail = 'Request failed';
    try {
      const body = await response.json();
      detail = body.detail || body.message || detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return response.json();
}

export async function checkHealth() {
  try {
    return await request('/api/health');
  } catch {
    return { status: 'unavailable' };
  }
}

export async function getConfig() {
  return request('/api/config');
}

export async function analyzeImage(file, params) {
  const form = new FormData();
  form.append('file', file);
  form.append('params', JSON.stringify(params));
  return request('/api/analyze', { method: 'POST', body: form });
}

export async function loadDemoResult() {
  const response = await fetch('/demo/demo_result.json');
  if (!response.ok) throw new Error('Demo data not found');
  const data = await response.json();
  return { ...data, mode: 'demo' };
}

export function isDemoMode() {
  return DEMO_MODE;
}

export function getApiBaseUrl() {
  return API_URL;
}

export function decodeBase64Image(base64) {
  return `data:image/png;base64,${base64}`;
}
