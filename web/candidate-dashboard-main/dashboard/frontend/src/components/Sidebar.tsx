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
        <div className="p-5 font-bold text-lg border-b border-slate-100 dark:border-slate-800 mb-4">
          Оценка кандидатов
        </div>

        <nav className="flex-1 px-3 space-y-1">

          <button
            onClick={() => onViewChange("dashboard")}
            className={`flex w-full items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
              currentView === "dashboard"
                ? "bg-indigo-50 text-indigo-600 font-bold dark:bg-indigo-900/20"
                : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
            }`}
          >
            <Users size={18} /> Дашборд
          </button>


          <button
            onClick={() => onViewChange("rating")}
            className={`flex w-full items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
              currentView === "rating"
                ? "bg-yellow-50 text-yellow-600 font-bold dark:bg-yellow-900/20"
                : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
            }`}
          >
            <Trophy size={18} /> Рейтинг
          </button>

          <hr className="my-4 border-slate-100 dark:border-slate-800" />


          <button
            onClick={() => setSettingsOpen(true)}
            className="flex w-full items-center gap-3 px-3 py-2 text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 rounded-lg transition-colors"
          >
            <Settings size={18} /> Настройки
          </button>


          <button
            onClick={() => {
              console.log("Жаңарту батырмасы басылды");
              onRefreshRequested();
            }}
            className="flex w-full items-center gap-3 px-3 py-2 text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 rounded-lg transition-colors"
          >
            <RefreshCw size={18} /> Обновить данные
          </button>
        </nav>
      </aside>


      <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </>
  );
}