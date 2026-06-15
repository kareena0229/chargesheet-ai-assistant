
"use client";

import { useState } from "react";

export default function Home() {

  const [file, setFile] = useState<File | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [classification, setClassification] = useState("");
  const [checklist, setChecklist] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [chatLoading, setChatLoading] = useState(false);


  // Upload + Analyze
  const handleUpload = async () => {

    if (!file) {
      alert("Please upload a chargesheet PDF");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {

      setLoading(true);

      // Analyze API
      const res = await fetch(
        "http://127.0.0.1:8001/api/analyze",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await res.json();

      setSummary(data.summary);
      setClassification(data.crime_type);
      setChecklist(data.checklist);

      // Upload to RAG
      await fetch(
        "http://127.0.0.1:8001/api/upload-rag",
        {
          method: "POST",
          body: formData,
        }
      );
      alert("Chargesheet processed successfully!");
      setLoading(false);

    } catch (err) {

      console.error(err);
      alert("Error connecting to backend");
      setLoading(false);

    }
  };


  // Chat Function
  const askQuestion = async () => {

    if (!question) return;

    setChatLoading(true);

    try {

      const res = await fetch(
        "http://127.0.0.1:8001/api/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question,
          }),
        }
      );

      const data = await res.json();

      setAnswer(data.answer);

    } catch (err) {

      console.error(err);
      setAnswer("Error fetching response.");

    }

    setChatLoading(false);
  };


  return (

    <main className="min-h-screen bg-slate-100 p-10">

      <h1 className="text-4xl font-bold text-slate-900 mb-10">
        ⚖️ Chargesheet AI Assistant
      </h1>


      {/* Upload Card */}
      <div className="bg-white border border-gray-300 p-6 rounded-xl shadow-lg mb-8">

        <p className="text-lg font-semibold text-slate-800 mb-4">
          Upload Chargesheet PDF
        </p>

        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="mb-4 block w-full text-sm text-slate-700"
        />

        <button
          onClick={handleUpload}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition"
        >
          {loading ? "Analyzing..." : "Analyze Chargesheet"}
        </button>

      </div>


      {/* Chat Section */}
      <div className="bg-white border border-gray-300 p-6 rounded-xl shadow-lg mb-8">

       <h2 className="text-2xl font-bold text-slate-900 mb-4">
          Chat With Chargesheet
        </h2>

        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask questions about the uploaded chargesheet..."
         className="w-full border border-gray-300 p-3 rounded-lg text-black placeholder-gray-500 bg-white"
        />

        <button
          onClick={askQuestion}
         className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg mt-4 transition"
        >
          {chatLoading ? "Thinking..." : "Ask AI"}
        </button>

        {answer && (
         <div className="mt-6 bg-gray-100 text-black p-4 rounded-lg whitespace-pre-wrap">
            {answer}
          </div>
        )}

      </div>


      {/* Summary */}
      {summary && (
<div className="bg-white border border-gray-300 p-6 rounded-xl shadow-lg mb-6 text-slate-900">
          <h2 className="text-xl font-bold text-slate-900 mb-3">
            Structured Case Summary
          </h2>

          <p>
            <strong>FIR Number:</strong> {summary.fir_number}
          </p>

          <p>
            <strong>Date:</strong> {summary.date}
          </p>

          <p>
            <strong>Police Station:</strong> {summary.police_station}
          </p>

          <p>
            <strong>Legal Sections:</strong> {summary.sections.join(", ")}
          </p>

        </div>

      )}


      {/* Classification */}
      {classification && (

<div className="bg-white border border-gray-300 p-6 rounded-xl shadow-lg mb-6 text-black">

          <h2 className="text-xl font-bold text-slate-900 mb-3">
            Crime Classification
          </h2>

          <p className="text-green-700 font-semibold text-lg">
            {classification}
          </p>

        </div>

      )}


      {/* Checklist */}
      {checklist.length > 0 && (

       <div className="bg-white border border-gray-300 p-6 rounded-xl shadow-lg text-black">

          <h2 className="text-xl font-bold text-slate-900 mb-4">
            Investigation Checklist
          </h2>

          {checklist.map((item: any, i: number) => (

            <div
              key={i}
              className="mb-3 flex justify-between items-center border-b pb-3"
            >

              <div>

                <p className="font-semibold text-slate-900">
                  {item.item}
                </p>

                {item.matched_text && (
                  <p className="text-sm text-gray-500">
                    Evidence: {item.matched_text}
                  </p>
                )}

              </div>


              {item.status === "PRESENT" && (
                <span className="bg-green-100 text-green-700 px-3 py-1 rounded-lg font-semibold">
                  ✅ Present
                </span>
              )}

              {item.status === "PARTIAL" && (
                <span className="bg-yellow-100 text-yellow-700 px-3 py-1 rounded-lg font-semibold">
                  ⚠ Partial
                </span>
              )}

              {item.status === "MISSING" && (
                <span className="bg-red-100 text-red-700 px-3 py-1 rounded-lg font-semibold">
                  ❌ Missing
                </span>
              )}

            </div>

          ))}

        </div>

      )}

    </main>

  );
}
