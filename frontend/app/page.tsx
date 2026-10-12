
"use client";

import { useState } from "react";

export default function Home() {
  const [url, setUrl] = useState("");
  const [shortUrl, setShortUrl] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setShortUrl("");
    setCopied(false);

    try {
      setLoading(true);

      const response = await fetch(
        "https://url-shortener-backend-njbi.onrender.com/shorten",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ url: url.trim() }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to shorten URL"
        );
      }

      if (!data.shortUrl) {
        throw new Error("Short URL not received from backend");
      }

      setShortUrl(data.shortUrl);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(shortUrl);
      setCopied(true);
    } catch {
      setError("Unable to copy URL. Please copy it manually.");
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-100 px-4 py-10">
      <div className="w-full max-w-xl bg-white rounded-2xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center mb-2">
          URL Shortener
        </h1>

        <p className="text-center text-gray-500 mb-8">
          Convert your long URL into a short URL
        </p>

        <form onSubmit={handleSubmit}>
          <label className="block mb-2 font-medium">
            Enter your URL
          </label>

          <input
            type="url"
            required
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/very-long-url"
            className="w-full border border-gray-300 rounded-lg px-4 py-3 outline-none focus:ring-2 focus:ring-blue-500"
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-4 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Shortening..." : "Shorten URL"}
          </button>
        </form>

        {error && (
          <div className="mt-6 bg-red-100 text-red-700 p-4 rounded-lg break-all">
            {error}
          </div>
        )}

        {shortUrl && (
          <div className="mt-6 bg-green-100 p-4 rounded-lg">
            <p className="font-medium mb-2">
              Your Short URL:
            </p>

            <a
              href={shortUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 underline break-all"
            >
              {shortUrl}
            </a>

            <button
              type="button"
              onClick={handleCopy}
              className="block mt-4 bg-green-700 text-white px-4 py-2 rounded-lg"
            >
              {copied ? "Copied!" : "Copy URL"}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
