import type { Notification, NotificationCreate, Token, UserCreate } from "../types";

const API_URL = import.meta.env.VITE_API_URL;
const TOKEN_KEY = "token";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export const getToken = () => sessionStorage.getItem(TOKEN_KEY);
export const saveToken = (token: string) => sessionStorage.setItem(TOKEN_KEY, token);
export const clearToken = () => sessionStorage.removeItem(TOKEN_KEY);

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (response.status === 401) clearToken();

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    // FastAPI: "detail" es un string en tus errores (404, 409, 422 de canal)
    // y una lista en los 422 de validación de Pydantic
    const message = typeof body?.detail === "string" ? body.detail : `Request failed (${response.status})`;
    throw new ApiError(response.status, message);
  }

  if (response.status === 204) return undefined as T; // DELETE no tiene body
  return response.json() as Promise<T>;
}

const json = (body: unknown): RequestInit => ({
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export const register = (data: UserCreate) =>
  request<unknown>("/auth/register", { method: "POST", ...json(data) });

export async function login(email: string, password: string): Promise<void> {
  const token = await request<Token>("/auth/token", {
    method: "POST",
    body: new URLSearchParams({ username: email, password }), // formulario, no JSON
  });
  saveToken(token.access_token);
}

export const listNotifications = () => request<Notification[]>("/notifications");

export const createNotification = (data: NotificationCreate) =>
  request<Notification>("/notifications", { method: "POST", ...json(data) });

export const deleteNotification = (id: number) =>
  request<void>(`/notifications/${id}`, { method: "DELETE" });