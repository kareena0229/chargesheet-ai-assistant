"use client";

import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a PDF file");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Backend error");
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      alert("Error connecting to backend.");
      console.error(error);
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-10">
      <h1 className="text-3xl font-bold mb-6 text-blue-700">
        ⚖️ Chargesheet AI Assistant
      </h1>

      <div className="bg-white p-6 rounded-xl shadow-md mb-8">
        <input
          type="file"
          accept=".pdf"
          onChange={(e) =>
            setFile(e.target.files ? e.target.files[0] : null)
          }
        />
        <button
          onClick={handleUpload}
          className="ml-4 bg-blue-600 text-white px-4 py-2 rounded-lg"
        >
          {loading ? "Analyzing..." : "Analyze Chargesheet"}
        </button>
      </div>

      {result && (
        <>
          <div className="bg-white p-6 rounded-xl shadow-md mb-6">
            <h2 className="text-xl font-semibold mb-3">
              Output A — Structured Summary
            </h2>
            <p><b>FIR:</b> {result.structured_summary.fir_number}</p>
            <p><b>Date:</b> {result.structured_summary.fir_date}</p>
            <p><b>Police Station:</b> {result.structured_summary.police_station}</p>
            <p><b>Legal Sections:</b> {result.structured_summary.legal_sections?.join(", ")}</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md mb-6">
            <h2 className="text-xl font-semibold mb-3">
              Output B — Crime Classification
            </h2>
            <p className="text-lg font-bold text-green-600">
              {result.crime_classification.display_name || "UNKNOWN"}
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md">
            <h2 className="text-xl font-semibold mb-3">
              Output C — Checklist
            </h2>
            <ul>
              {result.checklist_validation.map((item: any, index: number) => (
                <li key={index} className="mb-2">
                  {item.item} —{" "}
                  <span
                    className={
                      item.status === "PRESENT"
                        ? "text-green-600"
                        : "text-red-600"
                    }
                  >
                    {item.status}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}