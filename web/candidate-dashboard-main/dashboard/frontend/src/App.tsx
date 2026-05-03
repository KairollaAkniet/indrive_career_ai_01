import React, { useState, useEffect, useMemo, useCallback } from "react";
import Sidebar from "./components/Sidebar";
import { Trophy, Users, Loader2, Download, Search, FileText, X } from "lucide-react";
import axios from 'axios';


const API_BASE_URL = "http://127.0.0.1:8000";
const API_URL = import.meta.env.VITE_API_URL;
axios.get(`${import.meta.env.VITE_API_URL}`)

export default function App() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState("dashboard");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedAnalysis, setSelectedAnalysis] = useState<string | null>(null);


  const refreshCandidates = async () => {
    setLoading(true);
    try {
      const timestamp = new Date().getTime();
      const response = await fetch(`${API_BASE_URL}/api/candidates?t=${timestamp}`, {
        cache: 'no-store'
      });
      if (!response.ok) throw new Error("Серверге қосылу мүмкін болмады");
      const data = await response.json();
      setCandidates(data || []);
    } catch (error) {
      console.error("Жаңарту қатесі:", error);
    } finally {
      setLoading(false);
    }
  };


  const fetchSilent = useCallback(async () => {
    try {
      const timestamp = new Date().getTime();
      const response = await fetch(`${API_BASE_URL}/api/candidates?t=${timestamp}`, { cache: 'no-store' });
      if (response.ok) {
        const data = await response.json();
        setCandidates(data || []);
      }
    } catch (error) {
      console.error("Silent update fail");
    }
  }, []);

  useEffect(() => {
    refreshCandidates();
    const intervalId = setInterval(fetchSilent, 5000);
    return () => clearInterval(intervalId);
  }, [fetchSilent]);


  const exportData = () => {
    if (candidates.length === 0) return;
    const headers = "Rank,Full Name,Username,Score,Probability,Summary\n";
    const rows = candidates.map((c, i) =>
      `${i + 1},"${c.full_name}",@${c.username},${c.ai_score},${c.ai_probability || 0}%,"${(c.ai_summary || "").replace(/"/g, '""')}"`
    ).join("\n");
    const blob = new Blob(["\uFEFF" + headers + rows], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.setAttribute("download", `HR_Report_${new Date().toLocaleDateString()}.csv`);
    link.click();
  };


  const filteredCandidates = useMemo(() => {
    return candidates
      .filter(c => (c.full_name || "").toLowerCase().includes(searchTerm.toLowerCase()))
      .sort((a, b) => (b.ai_score || 0) - (a.ai_score || 0));
  }, [candidates, searchTerm]);

  const ratedCandidates = [...candidates].sort((a, b) => (b.ai_score || 0) - (a.ai_score || 0));
  const averageScore = candidates.length > 0
    ? (candidates.reduce((acc, curr) => acc + (curr.ai_score || 0), 0) / candidates.length).toFixed(1)
    : "0.0";

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-[#050510] text-slate-900 dark:text-white font-sans transition-colors duration-300">

      <Sidebar
        onRefreshRequested={refreshCandidates}
        onViewChange={setView}
        currentView={view}
      />

      <main className="flex-1 p-8 overflow-y-auto">
        {view === "dashboard" ? (
          <div className="max-w-6xl mx-auto animate-in fade-in duration-500">
            {/* Header */}
            <header className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h1 className="text-4xl font-black italic tracking-tighter text-indigo-600 dark:text-indigo-500 uppercase">
                  Talent Analytics
                </h1>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">AI-мен өңделген кандидаттар базасы</p>
              </div>

              <div className="flex items-center gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Аты бойынша іздеу..."
                    className="pl-10 pr-4 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-sm outline-none focus:ring-2 focus:ring-indigo-500 w-64 shadow-sm"
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <button onClick={exportData} className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-xl text-sm font-bold shadow-md transition-all active:scale-95">
                  <Download className="w-4 h-4" /> Export CSV
                </button>
              </div>
            </header>


            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
              <div className="bg-white dark:bg-slate-900 p-8 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm">
                <p className="text-slate-400 text-[10px] font-bold uppercase tracking-widest">Жалпы кандидаттар</p>
                <h3 className="text-5xl font-black mt-2">{candidates.length}</h3>
              </div>
              <div className="bg-white dark:bg-slate-900 p-8 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm">
                <p className="text-slate-400 text-[10px] font-bold uppercase tracking-widest">Орташа балл</p>
                <h3 className="text-5xl font-black mt-2 text-indigo-600 italic">{averageScore}</h3>
              </div>
              <div className="bg-white dark:bg-slate-900 p-8 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm">
                <p className="text-slate-400 text-[10px] font-bold uppercase tracking-widest">Үздік кандидат</p>
                <h3 className="text-5xl font-black mt-2 text-green-500 truncate">{ratedCandidates[0]?.full_name || "—"}</h3>
              </div>
            </div>


            <div className="bg-white dark:bg-slate-900/30 border border-slate-200 dark:border-slate-800 rounded-[2rem] overflow-hidden shadow-sm">
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead className="bg-slate-50/50 dark:bg-slate-800/30">
                    <tr className="border-b border-slate-100 dark:border-slate-800 text-[10px] uppercase font-bold text-slate-400">
                      <th className="p-6 text-center">Rank</th>
                      <th className="p-6">Кандидат</th>
                      <th className="p-6 text-center">AI Rating</th>
                      <th className="p-6 text-center">AI Detector</th>
                      <th className="p-6">AI Summary Analysis</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800/50">
                    {filteredCandidates.map((c, i) => (
                      <tr key={c.id} className="hover:bg-indigo-50/50 dark:hover:bg-indigo-500/5 transition-colors group">
                        <td className="p-6 text-center font-mono text-slate-300 dark:text-slate-600">#{i + 1}</td>
                        <td className="p-6">
                          <div className="font-bold text-lg text-slate-900 dark:text-white">{c.full_name}</div>
                          <div className="text-xs text-slate-400">@{c.username}</div>
                        </td>
                        <td className="p-6 text-center">
                          <div className={`inline-block px-4 py-2 rounded-2xl font-black text-xl ${
                            c.ai_score >= 70 ? "bg-green-100 text-green-600 dark:bg-green-500/10" : "bg-amber-100 text-amber-600 dark:bg-amber-500/10"
                          }`}>{c.ai_score}</div>
                        </td>
                        <td className="p-6">
                          <div className="flex flex-col items-center gap-1">
                            <span className="text-[10px] text-slate-400 font-bold">PROB: {c.ai_probability}%</span>
                            <div className="w-20 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                              <div className="h-full bg-indigo-500" style={{ width: `${c.ai_probability}%` }} />
                            </div>
                          </div>
                        </td>
                        <td className="p-6 max-w-xs">
                          <div
                            onClick={() => setSelectedAnalysis(c.ai_summary)}
                            className="flex gap-2 items-start cursor-pointer hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                          >
                            <FileText className="w-4 h-4 mt-1 flex-shrink-0 text-slate-300" />
                            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed italic line-clamp-2">
                              {c.ai_summary || "Талдау жоқ"}
                            </p>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {loading && <div className="p-10 text-center"><Loader2 className="w-8 h-8 animate-spin mx-auto text-indigo-500" /></div>}
            </div>
          </div>
        ) : (

          <div className="max-w-4xl mx-auto text-center py-10 animate-in slide-in-from-bottom-10">
            <Trophy className="w-24 h-24 text-yellow-500 mx-auto mb-6 drop-shadow-lg" />
            <h1 className="text-7xl font-black italic bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent uppercase tracking-tighter mb-16">
              Leaderboard
            </h1>
            <div className="space-y-4">
              {ratedCandidates.map((c, i) => (
                <div key={c.id} className={`flex items-center p-8 rounded-[2.5rem] border transition-all ${
                  i === 0 ? "bg-white border-yellow-400 scale-105 shadow-xl shadow-yellow-200" : "bg-white border-slate-100 shadow-sm"
                }`}>
                  <span className={`text-4xl font-black mr-10 ${i === 0 ? "text-yellow-500" : "text-slate-200"}`}>0{i + 1}</span>
                  <div className="flex-1 text-left">
                    <h3 className="text-2xl font-bold text-slate-900">{c.full_name}</h3>
                    <p className="text-slate-500 text-sm italic line-clamp-1">"{c.ai_summary}"</p>
                  </div>
                  <div className="text-4xl font-black text-indigo-600">{c.ai_score}%</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>


      {selectedAnalysis && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 p-8 rounded-[2rem] max-w-2xl w-full relative shadow-2xl animate-in zoom-in-95">
            <button onClick={() => setSelectedAnalysis(null)} className="absolute top-6 right-6 text-slate-400 hover:text-slate-900">
              <X className="w-6 h-6" />
            </button>
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-indigo-600">
              <FileText className="w-5 h-5" /> Толық AI талдау
            </h3>
            <div className="bg-slate-50 dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-800">
              <p className="text-slate-700 dark:text-slate-300 leading-relaxed italic text-lg">
                {selectedAnalysis}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}