import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/** Redirects to /login when unauthenticated; waits for the initial token check. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="status">Loading…</p>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
