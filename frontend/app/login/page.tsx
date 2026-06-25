"use client";
import Link from "next/link";
import { useState } from "react";
import { apiFetch } from "../lib/api";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!username) { setError("Please enter your username or email."); return; }
    if (!password) { setError("Please enter your password."); return; }

    setLoading(true);

    try {
      const data = await apiFetch("/login/", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      console.log("Login successful:", data);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');
        @import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        .if-root {
          min-height: 100vh;
          background: #05080f;
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: 'Sora', sans-serif;
          padding: 2rem;
          position: relative;
          overflow: hidden;
        }

        .grid-bg {
          position: absolute; inset: 0;
          background-image:
            linear-gradient(rgba(30,100,255,0.07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(30,100,255,0.07) 1px, transparent 1px);
          background-size: 36px 36px;
          pointer-events: none;
        }

        .glow-orb {
          position: absolute;
          width: 340px; height: 340px;
          background: radial-gradient(circle, rgba(30,100,255,0.18) 0%, transparent 70%);
          top: -60px; right: -60px;
          pointer-events: none;
          border-radius: 50%;
        }

        .glow-orb2 {
          position: absolute;
          width: 200px; height: 200px;
          background: radial-gradient(circle, rgba(0,200,180,0.1) 0%, transparent 70%);
          bottom: 20px; left: -40px;
          pointer-events: none;
          border-radius: 50%;
        }

        .card {
          position: relative;
          background: rgba(10,15,26,0.92);
          border: 1px solid rgba(30,100,255,0.25);
          border-radius: 20px;
          padding: 2.5rem 2.25rem;
          width: 100%; max-width: 420px;
          backdrop-filter: blur(12px);
          box-shadow: 0 0 0 1px rgba(30,100,255,0.08), 0 32px 80px rgba(0,0,0,0.7);
        }

        .card::before {
          content: '';
          position: absolute;
          top: 0; left: 10%; right: 10%;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(60,140,255,0.6), transparent);
          border-radius: 999px;
        }

        .brand {
          display: flex; align-items: center; gap: 10px;
          margin-bottom: 2rem;
        }

        .brand-icon {
          width: 36px; height: 36px;
          background: linear-gradient(135deg, #1a6fff, #0ef0c0);
          border-radius: 10px;
          display: flex; align-items: center; justify-content: center;
          flex-shrink: 0;
        }

        .brand-name {
          font-family: 'Space Mono', monospace;
          font-size: 15px;
          font-weight: 700;
          color: #e8f0ff;
          letter-spacing: 0.02em;
          display: block;
        }

        .brand-tag {
          font-family: 'Space Mono', monospace;
          font-size: 9px;
          color: #3c8cff;
          letter-spacing: 0.12em;
          text-transform: uppercase;
          display: block;
          margin-top: 1px;
        }

        .status-dots {
          display: flex; gap: 5px; align-items: center;
          margin-left: auto;
        }

        .dot {
          width: 5px; height: 5px; border-radius: 50%;
        }
        .dot-green { background: #0ef0c0; animation: pulse 1.6s ease-in-out infinite; }
        .dot-blue  { background: #3c8cff; }
        .dot-dim   { background: #1a3060; }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50%       { opacity: 0.35; }
        }

        .card-title {
          font-size: 22px;
          font-weight: 600;
          color: #ddeaff;
          margin-bottom: 4px;
          letter-spacing: -0.02em;
        }

        .card-sub {
          font-size: 13px;
          color: #4a6080;
          margin-bottom: 2rem;
          font-weight: 300;
        }

        .error-msg {
          display: flex; align-items: center; gap: 8px;
          background: rgba(200,50,50,0.1);
          border: 1px solid rgba(200,50,50,0.25);
          border-radius: 8px;
          padding: 9px 12px;
          margin-bottom: 1rem;
          font-size: 12px;
          color: #e07070;
        }

        .field { margin-bottom: 1.1rem; }

        .field label {
          display: block;
          font-size: 11px;
          font-weight: 500;
          color: #3c7ccc;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          margin-bottom: 7px;
        }

        .input-wrap { position: relative; }

        .input-wrap .i-icon {
          position: absolute; left: 13px; top: 50%; transform: translateY(-50%);
          color: #2a5090;
          font-size: 16px;
          pointer-events: none;
          transition: color 0.2s;
        }

        .input-wrap:focus-within .i-icon { color: #3c8cff; }

        .field input {
          width: 100%;
          background: rgba(10,20,45,0.8);
          border: 1px solid rgba(30,80,180,0.3);
          border-radius: 10px;
          color: #c8daff;
          font-family: 'Sora', sans-serif;
          font-size: 14px;
          padding: 11px 13px 11px 40px;
          outline: none;
          transition: border-color 0.2s, box-shadow 0.2s;
        }

        .field input::placeholder { color: #253555; }

        .field input:focus {
          border-color: rgba(60,140,255,0.7);
          box-shadow: 0 0 0 3px rgba(30,100,255,0.12);
        }

        .forgot {
          text-align: right;
          margin-top: -6px;
          margin-bottom: 1.4rem;
        }

        .forgot a {
          font-size: 12px;
          color: #2a5090;
          text-decoration: none;
          transition: color 0.2s;
        }
        .forgot a:hover { color: #3c8cff; }

        .btn-login {
          width: 100%;
          background: linear-gradient(135deg, #1a5eff 0%, #0a40cc 100%);
          border: none;
          border-radius: 10px;
          color: #fff;
          font-family: 'Sora', sans-serif;
          font-size: 14px;
          font-weight: 600;
          padding: 12px;
          cursor: pointer;
          letter-spacing: 0.04em;
          position: relative;
          overflow: hidden;
          transition: transform 0.15s, box-shadow 0.2s, opacity 0.2s;
          box-shadow: 0 4px 24px rgba(30,100,255,0.35);
          display: flex; align-items: center; justify-content: center; gap: 8px;
        }

        .btn-login::after {
          content: '';
          position: absolute; inset: 0;
          background: linear-gradient(135deg, rgba(255,255,255,0.08), transparent);
          pointer-events: none;
        }

        .btn-login:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 8px 32px rgba(30,100,255,0.45);
        }

        .btn-login:active:not(:disabled) { transform: scale(0.99); }
        .btn-login:disabled { opacity: 0.6; cursor: not-allowed; }

        .spinner {
          width: 14px; height: 14px;
          border: 2px solid rgba(255,255,255,0.3);
          border-top-color: #fff;
          border-radius: 50%;
          animation: spin 0.7s linear infinite;
          flex-shrink: 0;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        .divider {
          display: flex; align-items: center; gap: 12px;
          margin: 1.4rem 0;
        }
        .divider::before, .divider::after {
          content: ''; flex: 1;
          height: 1px;
          background: rgba(30,80,180,0.2);
        }
        .divider span {
          font-size: 11px; color: #2a4060;
          font-family: 'Space Mono', monospace;
          letter-spacing: 0.05em;
        }

        .sso-btn {
          width: 100%;
          background: rgba(10,20,45,0.6);
          border: 1px solid rgba(30,80,180,0.25);
          border-radius: 10px;
          color: #5a80b0;
          font-family: 'Sora', sans-serif;
          font-size: 13px;
          padding: 10px;
          cursor: pointer;
          display: flex; align-items: center; justify-content: center; gap: 8px;
          transition: border-color 0.2s, color 0.2s;
        }

        .sso-btn:hover {
          border-color: rgba(60,140,255,0.5);
          color: #a0c0ff;
        }

        .footer-link {
          text-align: center;
          margin-top: 1.4rem;
          font-size: 12px;
          color: #2a4060;
        }

        .footer-link a {
          color: #3c7ccc;
          text-decoration: none;
          font-weight: 500;
          transition: color 0.2s;
        }

        .footer-link a:hover { color: #6aadff; }
      `}</style>

      <main className="if-root">
        <div className="grid-bg" aria-hidden="true" />
        <div className="glow-orb" aria-hidden="true" />
        <div className="glow-orb2" aria-hidden="true" />

        <div className="card">
          {/* Brand */}
          <div className="brand">
            <div className="brand-icon" aria-hidden="true">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                <polyline
                  points="1,14 5,8 8,11 12,4 17,7"
                  stroke="white"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  fill="none"
                />
                <circle cx="17" cy="7" r="1.5" fill="white" />
              </svg>
            </div>
            <div>
              <span className="brand-name">InsightFlow</span>
              <span className="brand-tag">Analytics Platform</span>
            </div>
            <div className="status-dots" aria-label="System status: online">
              <div className="dot dot-green" />
              <div className="dot dot-blue" />
              <div className="dot dot-dim" />
            </div>
          </div>

          <h1 className="card-title">Welcome back</h1>
          <p className="card-sub">Sign in to access your analytics dashboard</p>

          {/* Error */}
          {error && (
            <div className="error-msg" role="alert">
              <i className="ti ti-alert-circle" aria-hidden="true" style={{ fontSize: 15, flexShrink: 0 }} />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleLogin} noValidate>
            <div className="field">
              <label htmlFor="username">Username</label>
              <div className="input-wrap">
                <input
                  id="username"
                  type="text"
                  placeholder="your@email.com"
                  autoComplete="username"
                  value={username}
                  onChange={(e) => { setUsername(e.target.value); setError(""); }}
                />
                <i className="ti ti-user i-icon" aria-hidden="true" />
              </div>
            </div>

            <div className="field">
              <label htmlFor="password">Password</label>
              <div className="input-wrap">
                <input
                  id="password"
                  type="password"
                  placeholder="••••••••••"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setError(""); }}
                />
                <i className="ti ti-lock i-icon" aria-hidden="true" />
              </div>
            </div>

            <div className="forgot">
              <Link href="/forgot-password">Forgot password?</Link>
            </div>

            <button className="btn-login" type="submit" disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner" />
                  Authenticating...
                </>
              ) : (
                "Sign in to Dashboard"
              )}
            </button>
          </form>

          <div className="divider"><span>or</span></div>

          <button className="sso-btn" type="button">
            <i className="ti ti-building" aria-hidden="true" style={{ fontSize: 16 }} />
            Continue with SSO
          </button>

          <p className="footer-link">
            No account? <Link href="/request-access">Request access</Link>
          </p>
        </div>
      </main>
    </>
  );
}