import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiErrorMessage } from "../api/client";
import { register } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";

/** Client-side rules mirror the backend: username ≥3, valid email, password ≥8. */
function validate(username: string, email: string, password: string): string | null {
  if (username.trim().length < 3) return "Username must be at least 3 characters";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return "Enter a valid email address";
  if (password.length < 8) return "Password must be at least 8 characters";
  return null;
}

export function RegisterPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const clientError = validate(username, email, password);
    if (clientError) {
      setError(clientError);
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      await register({ username: username.trim(), email, password });
      await login({ username: username.trim(), password }); // auto-login after register
      navigate("/");
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <h1>Register</h1>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Username
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoComplete="username"
          />
        </label>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="new-password"
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "Creating account…" : "Register"}
        </button>
      </form>
      <p>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}
