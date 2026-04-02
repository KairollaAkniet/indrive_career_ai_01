import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import { Trophy, Users, Loader2, AlertCircle } from "lucide-react";

// 🛠 ОСЫ ЖЕРГЕ ӨЗ IP-АДРЕСІҢДІ ЖАЗ:
const YOUR_IP = "192.168.10.88";
const API_BASE_URL = `http://192.168.10.88:8000`;

export default function App() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState("dashboard");

  const refreshCandidates = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/candidates`);
      if (!response.ok) throw new Error("Backend қосылмаған");
      const data = await response.json();
      setCandidates(data.candidates || []);
    } catch (error) {
      console.error("Fetch error:", error);
      setCandidates([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshCandidates();
  }, []);

  // 1. Дашборд үшін ID бойынша сұрыптау (1, 2, 3, 4 ретімен тұруы үшін)
  const sortedById = [...candidates].sort((a, b) => a.id - b.id);

  // 2. Рейтинг үшін Score бойынша сұрыптау (Ең жоғары ұпай бірінші)
  const ratedCandidates = [...candidates].sort((a, b) => b.ai_score - a.ai_score);

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors font-sans text-slate-900 dark:text-white">
      <Sidebar
        onRefreshRequested={refreshCandidates}
        onViewChange={setView}
        currentView={view}
      />

      <main className="flex-1 p-8 overflow-y-auto">
        {view === "dashboard" ? (
          <div className="animate-in fade-in duration-500 max-w-6xl mx-auto">
            <header className="mb-8 flex justify-between items-center">
              <div>
                <h1 className="font-bold text-3xl tracking-tight">Дашборд кандидатов</h1>
                <p className="text-slate-400 text-sm mt-1">Барлық тіркелген пайдаланушылар тізімі</p>
              </div>
              {loading && <Loader2 className="animate-spin text-indigo-500" />}
            </header>

            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50 dark:bg-slate-800/50 text-slate-500 text-xs uppercase font-bold">
                      <th className="px-6 py-4 w-16">ID</th>
                      <th className="px-6 py-4">Кандидат</th>
                      <th className="px-6 py-4 text-center">Score</th>
                      <th className="px-6 py-4">AI Summary</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {sortedById.length > 0 ? (
                      sortedById.map((c) => (
                        <tr key={c.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                          <td className="px-6 py-4 text-sm font-medium text-slate-400">{c.id}</td>
                          <td className="px-6 py-4">
                            <div className="font-bold">{c.full_name}</div>
                            <div className="text-xs font-normal text-slate-400">@{c.username}</div>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <span className={`inline-block px-3 py-1 rounded-full font-black text-sm ${
                              c.ai_score >= 70 ? "bg-green-50 text-green-600 dark:bg-green-900/20" :
                              c.ai_score >= 40 ? "bg-indigo-50 text-indigo-600 dark:bg-indigo-900/20" :
                              "bg-slate-100 text-slate-400 dark:bg-slate-800"
                            }`}>
                              {c.ai_score}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-xs text-slate-500 dark:text-slate-400 max-w-md leading-relaxed">
                            {c.ai_summary || "Талдау жасалмаған"}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={4} className="px-6 py-20 text-center">
                          {loading ? (
                            <div className="flex flex-col items-center gap-2">
                              <Loader2 className="animate-spin text-indigo-500" />
                              <span className="text-slate-400 text-sm">Деректер жүктелуде...</span>
                            </div>
                          ) : (
                            <div className="flex flex-col items-center gap-2 text-slate-400">
                              <AlertCircle className="w-8 h-8 opacity-20" />
                              <p>Кандидаттар табылмады немесе API қосылмаған.</p>
                            </div>
                          )}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto text-center animate-in slide-in-from-bottom-4 duration-500">
            <div className="mb-10">
              <Trophy className="w-16 h-16 text-yellow-500 mx-auto mb-4 drop-shadow-lg" />
              <h1 className="text-5xl font-black tracking-tighter italic uppercase text-slate-900 dark:text-white">TOP RANKING</h1>
              <p className="text-slate-400 mt-2">Ең үздік AI нәтижелері</p>
            </div>

            <div className="space-y-4 pb-10">
              {ratedCandidates.map((c, index) => (
                <div
                  key={c.id}
                  className={`flex items-center p-6 rounded-2xl border-2 transition-all hover:scale-[1.01] ${
                    index === 0
                      ? "bg-yellow-50/50 dark:bg-yellow-900/10 border-yellow-200 dark:border-yellow-900/50"
                      : "bg-white dark:bg-slate-900 border-slate-100 dark:border-slate-800"
                  }`}
                >
                  <div className={`text-3xl font-black mr-8 w-10 ${index === 0 ? "text-yellow-500" : "text-slate-300 dark:text-slate-700"}`}>
                    #{index + 1}
                  </div>

                  <div className="flex-1 text-left overflow-hidden">
                    <h3 className="font-bold text-xl mb-1">{c.full_name}</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed italic">
                      {c.ai_summary}
                    </p>
                  </div>

                  <div className="text-3xl font-black text-indigo-600 dark:text-indigo-400 ml-6">
                    {c.ai_score}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}