import axios, { AxiosError } from "axios";
import type { ApiError } from "../types";

export const TOKEN_KEY = "devlog_token";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api",
});

// Attach JWT from localStorage to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// On 401 (expired/invalid token) drop the token and send the user to /login
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401 && window.location.pathname !== "/login") {
      localStorage.removeItem(TOKEN_KEY);
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

/** Extract a human-readable message from a FastAPI error response. */
export function apiErrorMessage(error: unknown): string {
  if (axios.isAxiosError<ApiError>(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((d) => d.msg).join("; ");
    return error.message;
  }
  return "Something went wrong";
}
