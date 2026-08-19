import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function App() {
  const [status, setStatus] = useState<string>("未检查");
  const [result, setResult] = useState<string>("");

  async function checkBackend() {
    setStatus("检查中...");
    try {
      const response = await fetch(`${API_BASE}/health`);
      const data = await response.json();
      setStatus(data.ok ? "后端正常" : "后端异常");
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      setStatus("连接失败");
      setResult(String(error));
    }
  }

  async function inspectExcel(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    setResult("正在读取表格...");
    try {
      const response = await fetch(`${API_BASE}/files/inspect-excel`, {
        method: "POST",
        body: form,
      });
      const data = await response.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      setResult(String(error));
    }
  }

  return (
    <main>
      <aside>
        <h1>HitPaw Outreach</h1>
        <p>云端外联工作台 V1</p>
      </aside>

      <section>
        <div className="toolbar">
          <button onClick={checkBackend}>检查后端</button>
          <label>
            上传 Excel
            <input type="file" accept=".xlsx,.xlsm" onChange={inspectExcel} />
          </label>
        </div>

        <div className="panel">
          <h2>状态</h2>
          <p>{status}</p>
        </div>

        <div className="panel">
          <h2>输出</h2>
          <pre>{result || "先检查后端，或上传一个 Excel 表格。"}</pre>
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
