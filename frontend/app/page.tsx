"use client";

import { useState, useEffect, useRef } from "react";

const INTERESTS = [
  { label: "Large Language Models (LLMs)", icon: "🧠" },
  { label: "Computer Vision", icon: "👁️" },
  { label: "Robotics & Autonomous Systems", icon: "🤖" },
  { label: "AI Research Papers", icon: "📄" },
  { label: "Open-Source AI Tools", icon: "🛠️" },
  { label: "AI for Web Development", icon: "💻" },
  { label: "Machine Learning Ops (MLOps)", icon: "⚙️" },
  { label: "Generative AI & Creative AI", icon: "✨" },
];

function Particle({ x, y, color }: { x: number; y: number; color: string }) {
  const tx = `${(Math.random() - 0.5) * 120}px`;
  const ty = `${(Math.random() - 0.5) * 120}px`;
  const size = Math.random() * 6 + 4;
  return (
    <div
      className="particle"
      style={{
        left: x,
        top: y,
        width: size,
        height: size,
        background: color,
        ["--tx" as string]: tx,
        ["--ty" as string]: ty,
      }}
    />
  );
}

function SuccessScreen({ name }: { name: string }) {
  const colors = ["#7c3aed", "#4f46e5", "#2563eb", "#10b981", "#c4b5fd", "#60a5fa"];
  const particles = Array.from({ length: 18 }, (_, i) => ({
    id: i,
    x: `${40 + Math.random() * 20}%`,
    y: `${30 + Math.random() * 40}%`,
    color: colors[i % colors.length],
  }));

  return (
    <div className="success-card flex flex-col items-center justify-center py-8 relative overflow-hidden text-center">
      {particles.map((p) => (
        <Particle key={p.id} x={p.x as any} y={p.y as any} color={p.color} />
      ))}

      {/* Pulsing ring */}
      <div className="relative flex items-center justify-center mb-6">
        <div
          className="pulse-ring absolute w-20 h-20 rounded-full"
          style={{ border: "2px solid rgba(139,92,246,0.6)" }}
        />
        <div
          className="pulse-ring absolute w-20 h-20 rounded-full"
          style={{ border: "2px solid rgba(59,130,246,0.4)", animationDelay: "0.5s" }}
        />
        <div className="success-icon relative z-10 text-6xl">🤖</div>
      </div>

      <h2 className="text-2xl font-bold text-white mb-2">
        You&apos;re on board,{" "}
        <span className="gradient-text">{name.split(" ")[0]}!</span>
      </h2>
      <p className="text-slate-400 text-sm max-w-xs leading-relaxed">
        Your personalized AI briefing is now being prepared by our agents. Check
        your inbox daily at{" "}
        <span className="text-violet-400 font-semibold">11:30 AM IST</span> ☀️
      </p>

      <div className="mt-6 flex items-center gap-2 text-xs text-slate-500">
        <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block animate-pulse" />
        Agents are live &amp; monitoring the AI landscape
      </div>
    </div>
  );
}

export default function Home() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [interests, setInterests] = useState<string[]>([]);
  const [status, setStatus] = useState<{
    type: "success" | "error" | null;
    message: string;
  }>({ type: null, message: "" });
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submittedName, setSubmittedName] = useState("");

  const toggleInterest = (interest: string) => {
    setInterests((prev) =>
      prev.includes(interest)
        ? prev.filter((i) => i !== interest)
        : [...prev, interest]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || interests.length === 0) {
      setStatus({
        type: "error",
        message: "Please fill out all fields and select at least one interest.",
      });
      return;
    }

    setLoading(true);
    setStatus({ type: null, message: "" });

    try {
      const res = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, interests }),
      });

      const data = await res.json();

      if (res.ok) {
        setSubmittedName(name);
        setSubmitted(true);
        setName("");
        setEmail("");
        setInterests([]);
      } else {
        setStatus({
          type: "error",
          message: data.message || "An error occurred. Please try again.",
        });
      }
    } catch {
      setStatus({
        type: "error",
        message: "Network error. Please try again later.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Background */}
      <div className="stars-bg" />
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />

      <main className="relative z-10 min-h-screen flex items-center justify-center p-4 py-12">
        <div className="glass-card circuit-bg rounded-3xl max-w-2xl w-full p-8 md:p-10">

          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-block mb-4">
              <span className="ai-badge">POWERED BY MULTI-AGENT AI</span>
            </div>

            {/* Floating robot */}
            <div className="scan-line inline-block mb-4 text-6xl leading-none robot-float">
              🤖
            </div>

            <h1
              className="text-4xl md:text-5xl font-bold text-white mb-3 leading-tight"
              style={{ fontFamily: "'Space Grotesk', sans-serif" }}
            >
              AI{" "}
              <span className="gradient-text">Radar</span>
            </h1>
            <p className="text-slate-400 text-base max-w-sm mx-auto leading-relaxed">
              Get a daily curated AI newsletter, personalized to your interests
              and delivered every morning.
            </p>

            {/* Live indicator */}
            <div className="flex items-center justify-center gap-2 mt-4 text-xs text-slate-500">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Agents running 24/7
              <span className="mx-2 text-slate-700">•</span>
              <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
              Delivered at 11:30 AM IST
            </div>
          </div>

          {/* Divider */}
          <div
            className="w-full h-px mb-8"
            style={{
              background:
                "linear-gradient(90deg, transparent, rgba(139,92,246,0.3), transparent)",
            }}
          />

          {/* Success or Form */}
          {submitted ? (
            <SuccessScreen name={submittedName} />
          ) : (
            <>
              {/* Error message */}
              {status.type === "error" && (
                <div className="mb-5 px-4 py-3 rounded-xl text-sm text-red-300 border border-red-500/20 bg-red-500/10 flex items-center gap-2">
                  <span>⚠️</span> {status.message}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Name */}
                <div>
                  <label
                    htmlFor="name"
                    className="block text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2"
                  >
                    Full Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="ai-input w-full px-4 py-3 rounded-xl text-sm"
                    placeholder="Grishmank Parate"
                    required
                  />
                </div>

                {/* Email */}
                <div>
                  <label
                    htmlFor="email"
                    className="block text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2"
                  >
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="ai-input w-full px-4 py-3 rounded-xl text-sm"
                    placeholder="you@gmail.com"
                    required
                  />
                </div>

                {/* Interests */}
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">
                    Your AI Interests{" "}
                    {interests.length > 0 && (
                      <span className="ml-2 text-violet-400 normal-case tracking-normal font-normal">
                        ({interests.length} selected)
                      </span>
                    )}
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {INTERESTS.map(({ label, icon }) => {
                      const isSelected = interests.includes(label);
                      return (
                        <button
                          key={label}
                          type="button"
                          onClick={() => toggleInterest(label)}
                          className={`interest-card rounded-xl px-4 py-3 flex items-center gap-3 text-left w-full ${
                            isSelected ? "selected" : ""
                          }`}
                        >
                          <span className="text-lg leading-none">{icon}</span>
                          <span
                            className={`text-sm font-medium transition-colors ${
                              isSelected ? "text-violet-300" : "text-slate-400"
                            }`}
                          >
                            {label}
                          </span>
                          {isSelected && (
                            <span className="ml-auto text-violet-400 text-xs">✓</span>
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Submit */}
                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full text-white font-semibold py-3.5 px-6 rounded-xl text-sm transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-60 ${
                    loading ? "shimmer-btn" : "glow-btn"
                  }`}
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg
                        className="animate-spin w-4 h-4"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                        />
                      </svg>
                      Activating your AI agent...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-2">
                      🚀 Subscribe to AI Radar
                    </span>
                  )}
                </button>

                <p className="text-center text-xs text-slate-600">
                  No spam. Unsubscribe any time. Emails delivered at 11:30 AM IST.
                </p>
              </form>
            </>
          )}
        </div>
      </main>
    </>
  );
}
