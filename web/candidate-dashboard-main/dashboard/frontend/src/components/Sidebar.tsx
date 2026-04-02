import React, { useState } from "react";
import { RefreshCw, Settings, Trophy, Users } from "lucide-react";
import SettingsModal from "./SettingsModal";

type Props = {
  onRefreshRequested: () => void;
  onViewChange: (view: string) => void;
  currentView: string;
};

export default function Sidebar({ onRefreshRequested, onViewChange, currentView }: Props) {
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <>
      <aside className="w-64 border-r bg-white dark:bg-slate-950/60 border-slate-200 dark:border-slate-800 h-screen flex flex-col">
        <div className="p-5 font-bold text-lg">Оценка кандидатов</div>
        <nav className="flex-1 px-3 space-y-1">
          <button onClick={() => onViewChange("dashboard")} className={`flex w-full items-center gap-3 px-3 py-2 rounded-lg ${currentView === "dashboard" ? "bg-indigo-50 text-indigo-600 font-bold" : "text-slate-600"}`}>
            <Users size={18} /> Дашборд
          </button>
          <button onClick={() => onViewChange("rating")} className={`flex w-full items-center gap-3 px-3 py-2 rounded-lg ${currentView === "rating" ? "bg-yellow-50 text-yellow-600 font-bold" : "text-slate-600"}`}>
            <Trophy size={18} /> Рейтинг
          </button>
          <hr className="my-4" />
          <button onClick={() => setSettingsOpen(true)} className="flex w-full items-center gap-3 px-3 py-2 text-slate-700 hover:bg-slate-100 rounded-lg">
            <Settings size={18} /> Настройки
          </button>
          <button onClick={onRefreshRequested} className="flex w-full items-center gap-3 px-3 py-2 text-slate-700 hover:bg-slate-100 rounded-lg">
            <RefreshCw size={18} /> Обновить данные
          </button>
        </nav>
      </aside>
      <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </>
  );
}