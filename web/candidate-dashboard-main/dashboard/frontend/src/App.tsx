import { useEffect, useState, useCallback } from 'react';
import Sidebar from "./components/Sidebar";
import StatsCards from "./components/StatsCards";
import CandidatesTable from "./components/CandidatesTable";
import { fetchCandidates } from "./api/client";

export default function App() {
  const [userScore, setUserScore] = useState<string | number>(0);
  const [userName, setUserName] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);

  const refreshCandidates = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchCandidates();
      setCandidates(data || []);
    } catch (e) {
      console.log("Ошибка загрузки данных, но мы продолжаем...");
      setCandidates([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshCandidates();
    const params = new URLSearchParams(window.location.search);
    const score = params.get('score');
    const name = params.get('name');
    if (score) setUserScore(score);
    if (name) setUserName(name);
  }, [refreshCandidates]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="flex">
        <Sidebar onRefreshRequested={refreshCandidates} />
        <main className="flex-1 p-6">
          <header className="mb-8">
            <h1 className="text-2xl font-bold">
              {userName ? `Привет, ${userName}! Твой балл: ${userScore}` : "Дашборд кандидатов"}
            </h1>
          </header>
          <StatsCards candidates={candidates} loading={loading} />
          <CandidatesTable candidates={candidates} loading={loading} onRefresh={refreshCandidates} />
        </main>
      </div>
    </div>
  );
}

