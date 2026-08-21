"use client";

import { useState } from "react";

const INTERESTS = [
  "Large Language Models (LLMs)",
  "Computer Vision",
  "Robotics & Autonomous Systems",
  "AI Research Papers",
  "Open-Source AI Tools",
  "AI for Web Development",
  "Machine Learning Ops (MLOps)",
  "Generative AI & Creative AI"
];

export default function Home() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [interests, setInterests] = useState<string[]>([]);
  const [status, setStatus] = useState<{ type: 'success' | 'error' | null, message: string }>({ type: null, message: '' });
  const [loading, setLoading] = useState(false);

  const toggleInterest = (interest: string) => {
    setInterests(prev => 
      prev.includes(interest) 
        ? prev.filter(i => i !== interest)
        : [...prev, interest]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || interests.length === 0) {
      setStatus({ type: 'error', message: 'Please fill out all fields and select at least one interest.' });
      return;
    }

    setLoading(true);
    setStatus({ type: null, message: '' });

    try {
      const res = await fetch('/api/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, interests }),
      });

      const data = await res.json();

      if (res.ok) {
        setStatus({ type: 'success', message: 'Successfully subscribed to AI Radar!' });
        setName('');
        setEmail('');
        setInterests([]);
      } else {
        setStatus({ type: 'error', message: data.message || 'An error occurred. Please try again.' });
      }
    } catch {
      setStatus({ type: 'error', message: 'Network error. Please try again later.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-2xl w-full p-8 md:p-12">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">AI Radar</h1>
          <p className="text-lg text-gray-600">Get a daily curated AI newsletter powered by multi-agent AI</p>
        </div>

        {status.message && (
          <div className={`mb-6 p-4 rounded-lg ${status.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
            {status.message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              placeholder="Your Name"
              required
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              placeholder="your@email.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Select your AI Interests</label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {INTERESTS.map((interest) => (
                <label key={interest} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition">
                  <input
                    type="checkbox"
                    checked={interests.includes(interest)}
                    onChange={() => toggleInterest(interest)}
                    className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">{interest}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Subscribing...' : 'Subscribe to AI Radar'}
          </button>
        </form>
      </div>
    </main>
  );
}
