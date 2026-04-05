import React, { useState, useEffect, useMemo } from "react";
import Sidebar from "./components/Sidebar";
import { Trophy, Users, Loader2, Download, Search, FileText } from "lucide-react";

// ✅ Бэкенд адресін бір жерде ғана дұрыс анықтаймыз
const API_BASE_URL = "http://192.168.8.230:8000";

export default function App() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState("dashboard");
  const [searchTerm, setSearchTerm] = useState("");

  // ✅ Деректерді алу функциясы (Fetch қолданамыз)
  const refreshCandidates = async () => {
    setLoading(true);
    try {
      // Адрес: http://192.168.8.230:8000/api/candidates
      const response = await fetch(`${API_BASE_URL}/api/candidates`);
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();

      // Бэкенд CandidatesListOut форматында { candidates: [...] } қайтарады
      setCandidates(data.candidates || []);
    } catch (error) {
      console.error("Fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  // Алғаш рет жүктелгенде деректерді алу
  useEffect(() => {
    refreshCandidates();
  }, []);

  // CSV-ге экспорттау
  const exportData = () => {
    if (candidates.length === 0) return;
    const headers = "ID,Full Name,Username,Score,AI Probability,AI Summary\n";
    const rows = candidates.map(c =>
      `${c.id},"${c.full_name}",@${c.username},${c.ai_score},${c.ai_probability || 0}%,"${(c.ai_summary || "").replace(/"/g, '""')}"`
    ).join("\n");

    const BOM = "\uFEFF";
    const csvContent = BOM + headers + rows;
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.setAttribute("download", `HR_Report_${new Date().toLocaleDateString()}.csv`);
    link.click();
  };

  // Іздеу және сұрыптау
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
    <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors font-sans text-slate-900 dark:text-white">
      <Sidebar onRefreshRequested={refreshCandidates} onViewChange={setView} currentView={view} />

      <main className="flex-1 p-8 overflow-y-auto">
        {view === "dashboard" ? (
          <div className="animate-in fade-in duration-700 max-w-6xl mx-auto">
            <header className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h1 className="font-black text-4xl tracking-tight mb-2 uppercase italic text-indigo-600">Talent Analytics</h1>
                <p className="text-slate-500 dark:text-slate-400 text-sm">AI-мен өңделген кандидаттар базасы</p>
              </div>

              <div className="flex items-center gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Аты бойынша іздеу..."
                    className="pl-10 pr-4 py-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 outline-none w-64 text-black dark:text-white"
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <button
                  onClick={exportData}
                  className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-xl text-sm font-bold shadow-lg shadow-indigo-500/20 transition-all active:scale-95"
                >
                  <Download className="w-4 h-4" /> Export CSV
                </button>
              </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 text-black">
              <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
                <p className="text-slate-500 text-xs uppercase font-bold tracking-wider mb-1">Жалпы кандидаттар</p>
                <h3 className="text-4xl font-black">{candidates.length}</h3>
              </div>
              <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
                <p className="text-slate-500 text-xs uppercase font-bold tracking-wider mb-1">Орташа балл</p>
                <h3 className="text-4xl font-black text-indigo-600">{averageScore}</h3>
              </div>
              <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
                <p className="text-slate-500 text-xs uppercase font-bold tracking-wider mb-1">Үздік кандидат</p>
                <h3 className="text-4xl font-black text-green-500 truncate">{ratedCandidates[0]?.full_name || "—"}</h3>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-xl overflow-hidden text-black dark:text-white">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50/50 dark:bg-slate-800/30 text-slate-400 text-[10px] uppercase font-black tracking-widest">
                      <th className="px-8 py-5 text-center">Rank</th>
                      <th className="px-8 py-5">Кандидат</th>
                      <th className="px-8 py-5 text-center">AI Rating</th>
                      <th className="px-8 py-5 text-center">AI Detector</th>
                      <th className="px-8 py-5">AI Summary Analysis</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {filteredCandidates.length > 0 ? (
                      filteredCandidates.map((c, index) => (
                        <tr key={c.id} className="hover:bg-indigo-50/20 dark:hover:bg-indigo-900/10 transition-colors">
                          <td className="px-8 py-6 text-sm font-mono text-slate-400 text-center">#{index + 1}</td>
                          <td className="px-8 py-6">
                            <div className="font-bold text-lg">{c.full_name}</div>
                            <div className="text-xs text-slate-400">@{c.username}</div>
                          </td>
                          <td className="px-8 py-6 text-center">
                            <div className={`inline-flex items-center justify-center w-12 h-12 rounded-2xl font-black text-lg ${
                              (c.ai_score || 0) >= 70 ? "bg-green-100 text-green-600 dark:bg-green-900/30" :
                              (c.ai_score || 0) >= 40 ? "bg-amber-100 text-amber-600 dark:bg-amber-900/30" :
                              "bg-red-100 text-red-600 dark:bg-red-900/30"
                            }`}>
                              {c.ai_score || 0}
                            </div>
                          </td>
                          <td className="px-8 py-6">
                            <div className="flex flex-col items-center gap-1">
                              <div className="text-[10px] uppercase font-bold text-slate-400">
                                AI Prob: {c.ai_probability ?? 0}%
                              </div>
                              <div className="w-24 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                                <div
                                  className={`h-full transition-all ${(c.ai_probability || 0) > 50 ? 'bg-red-500' : 'bg-indigo-500'}`}
                                  style={{ width: `${c.ai_probability ?? 0}%` }}
                                />
                              </div>
                              {(c.ai_probability || 0) > 60 && (
                                <span className="text-[9px] text-red-500 font-black animate-pulse">🚨 SUSPICIOUS</span>
                              )}
                            </div>
                          </td>
                          <td className="px-8 py-6">
                            <div className="flex gap-2 items-start max-w-md">
                              <FileText className="w-4 h-4 text-slate-300 mt-1 flex-shrink-0" />
                              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed italic line-clamp-2">
                                {c.ai_summary || "Талдау жасалмады"}
                              </p>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5} className="px-8 py-20 text-center text-slate-400 italic">
                          {loading ? <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" /> : "Кандидаттар табылмады"}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          /* Leaderboard */
          <div className="max-w-4xl mx-auto text-center animate-in slide-in-from-bottom-8 duration-700">
            <Trophy className="w-20 h-20 text-yellow-500 mx-auto mb-6 drop-shadow-2xl" />
            <h1 className="text-6xl font-black mb-12 italic bg-gradient-to-r from-yellow-500 to-orange-500 bg-clip-text text-transparent uppercase tracking-tighter">Leaderboard</h1>
            <div className="grid gap-4">
              {ratedCandidates.map((c, index) => (
                <div key={c.id} className={`flex items-center p-8 rounded-3xl border-2 transition-all ${
                  index === 0 ? "bg-yellow-50/50 dark:bg-yellow-900/10 border-yellow-200 shadow-xl shadow-yellow-500/5 scale-105" : "bg-white dark:bg-slate-900 border-slate-100 dark:border-slate-800"
                }`}>
                  <span className={`text-4xl font-black mr-10 ${index === 0 ? "text-yellow-500" : "text-slate-200"}`}>0{index + 1}</span>
                  <div className="flex-1 text-left">
                    <h3 className="font-bold text-2xl mb-1">{c.full_name}</h3>
                    <p className="text-sm text-slate-500 italic line-clamp-1">"{c.ai_summary}"</p>
                  </div>
                  <div className="text-4xl font-black text-indigo-600">{c.ai_score}%</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}