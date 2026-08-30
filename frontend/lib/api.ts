export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers || {}),
      },
    });
    const text = await res.text();
    let data: any = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = { detail: text };
    }
    if (!res.ok) {
      const detail = data?.detail || data?.message || res.statusText;
      throw new ApiError(typeof detail === 'string' ? detail : JSON.stringify(detail), res.status);
    }
    return data as T;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if ((err as Error).name === 'AbortError') {
      throw new ApiError('Request timed out. Is the backend running on port 8000?', 408);
    }
    throw new ApiError('Backend unreachable. Start uvicorn on port 8000.', 503);
  } finally {
    clearTimeout(timer);
  }
}
