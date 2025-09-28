import React, { useState } from "react";
import { Link, Routes, Route } from "react-router-dom";

function Layout({ children }) {
  return (
    <div style={{ padding: "1rem", maxWidth: 960, margin: "0 auto" }}>
      <h1>Scraper Test Hub</h1>
      <div style={{ marginBottom: "1rem", display: "flex", gap: 12 }}>
        <Link to="/">Home</Link>
        <Link to="/youtube">YouTube Scraper</Link>
        <Link to="/twitter">Twitter Scraper</Link>
      </div>
      {children}
    </div>
  );
}

function Home() {
  return (
    <Layout>
      <p>Choose a scraper:</p>
      <ul>
        <li><Link to="/youtube">YouTube Scraper</Link></li>
        <li><Link to="/twitter">Twitter Scraper</Link></li>
      </ul>
    </Layout>
  );
}

function Table({ columns, rows }) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            {columns.map(c => (
              <th key={c.key} style={{ borderBottom: "1px solid #ccc", padding: 6, textAlign: "left" }}>
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, idx) => (
            <tr key={idx} style={{ borderBottom: "1px solid #eee" }}>
              {columns.map(c => (
                <td key={c.key} style={{ padding: 6 }}>
                  {c.render ? c.render(r[c.key], r) : String(r[c.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function YoutubePage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  function getYoutubeId(url) {
    try {
      const u = new URL(url);
      if (u.hostname.includes("youtube.com")) return u.searchParams.get("v");
      if (u.hostname.includes("youtu.be")) return u.pathname.slice(1).split("/")[0];
    } catch {}
    return null;
  }
  function getThumb(url, fallbackFromApi) {
    // If API already provided thumbnail_url, use it; else derive from link
    if (fallbackFromApi) return fallbackFromApi;
    const id = getYoutubeId(url);
    return id ? `https://img.youtube.com/vi/${id}/hqdefault.jpg` : null;
  }

  async function runYoutube() {
    setLoading(true); setErr(""); setRows([]);
    try {
      const res = await fetch("http://localhost:8000/api/youtube/scrape?max_results=5");
      if (!res.ok) throw new Error(`API ${res.status}`);
      const json = await res.json();
      const flat = Object.entries(json.results).flatMap(([category, items]) =>
        items.map(v => ({ ...v, category }))
      );
      setRows(flat);
    } catch (e) {
      setErr(String(e.message || e));
    } finally {
      setLoading(false);
    }
  }

  const cols = [
  {
    key: "thumb",
    header: "Preview",
    render: (_, row) => {
      const thumb = getThumb(row.url, row.thumbnail_url); // <-- here
      return thumb ? (
        <a href={row.url} target="_blank" rel="noreferrer">
          <img src={thumb} alt={row.title} style={{ width: 120, height: "auto", borderRadius: 6 }} />
        </a>
      ) : null;
    }
  },
  { key: "title", header: "Title", render: (val, row) => <a href={row.url} target="_blank" rel="noreferrer">{val}</a> },
  { key: "channel", header: "Channel" },
  { key: "upload_time", header: "Uploaded" },
  { key: "category", header: "Category" },
];


  return (
    <Layout>
      <h2>YouTube Scraper</h2>
      <button onClick={runYoutube} disabled={loading}>
        {loading ? "Running…" : "Run YouTube Scraper"}
      </button>
      {err && <div style={{ color: "red", marginTop: 8 }}>{err}</div>}
      {rows.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <Table columns={cols} rows={rows} />
        </div>
      )}
    </Layout>
  );
}


function TwitterPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function runTwitter() {
    setLoading(true); setErr(""); setRows([]);
    try {
      const res = await fetch("http://localhost:8000/api/twitter/search?limit=10");
      if (!res.ok) throw new Error(`API ${res.status}`);
      const json = await res.json();
      setRows(json.items);
    } catch (e) {
      setErr(String(e.message || e));
    } finally {
      setLoading(false);
    }
  }

  const cols = [
    { key: "created_at", header: "Time" },
    { key: "lang", header: "Lang" },
    { key: "text", header: "Text",
      render: (val, row) => <a href={row.url} target="_blank" rel="noreferrer">{val}</a> },
    { key: "likes", header: "Likes" },
    { key: "retweets", header: "RTs" }
  ];

  return (
    <Layout>
      <h2>Twitter Scraper</h2>
      <button onClick={runTwitter} disabled={loading}>
        {loading ? "Running…" : "Run Twitter Scraper"}
      </button>
      {err && <div style={{ color: "red", marginTop: 8 }}>{err}</div>}
      {rows.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <Table columns={cols} rows={rows} />
        </div>
      )}
    </Layout>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/youtube" element={<YoutubePage />} />
      <Route path="/twitter" element={<TwitterPage />} />
    </Routes>
  );
}
