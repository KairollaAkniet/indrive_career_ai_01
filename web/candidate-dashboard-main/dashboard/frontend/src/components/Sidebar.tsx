import { LayoutDashboard, RefreshCw, Settings } from "lucide-react";
import React from "react";

type Props = {
  onRefreshRequested?: () => void;
};

export default function Sidebar({ onRefreshRequested }: Props) {
  return (
    <aside className="w-64 shrink-0 border-r border-slate-800 bg-slate-950/60">
      <div className="p-5">
        <div className="text-lg font-semibold tracking-tight">
          Оценка кандидатов
        </div>
        <div className="mt-1 text-xs text-slate-400">
          Telegram bot | FastAPI | Dashboard
        </div>
      </div>

      <nav className="px-3 pb-4">
        <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-slate-200 hover:bg-slate-800/60">
          <LayoutDashboard size={18} />
          Дашборд
        </button>

        <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-slate-200 hover:bg-slate-800/60">
          <Settings size={18} />
          Настройки
        </button>

        <button
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-slate-200 hover:bg-slate-800/60"
          onClick={onRefreshRequested}
        >
          <RefreshCw size={18} />
          Обновить данные
        </button>
      </nav>
    </aside>
  );
}

