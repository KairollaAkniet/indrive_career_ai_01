import React from "react";
import { BadgeCheck, Clock, Users } from "lucide-react";
import type { Candidate } from "../api/types";

type Props = {
  candidates: Candidate[];
  loading?: boolean;
};

function formatAvg(scoreSum: number, count: number) {
  if (count <= 0) return "0.0";
  return (scoreSum / count).toFixed(1);
}

export default function StatsCards({ candidates, loading }: Props) {
  const total = candidates.length;
  const scoreSum = candidates.reduce((acc, c) => acc + (c.ai_score ?? 0), 0);

  // "Ожидают проверки" — кандидаты между низким и высоким порогом.
  // (Можно поменять правило под вашу бизнес-логику.)
  const pending = candidates.filter((c) => c.ai_score >= 50 && c.ai_score <= 80).length;
  const avg = formatAvg(scoreSum, total);

  return (
    <section className="grid gap-4 sm:grid-cols-3">
      <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-5 shadow-soft">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-sm text-slate-400">Всего заявок</div>
            <div className="mt-2 text-2xl font-semibold">{loading ? "—" : total}</div>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2">
            <Users size={18} />
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-5 shadow-soft">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-sm text-slate-400">Средний балл</div>
            <div className="mt-2 text-2xl font-semibold">{loading ? "—" : avg}</div>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2">
            <BadgeCheck size={18} />
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-5 shadow-soft">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-sm text-slate-400">Ожидают проверки</div>
            <div className="mt-2 text-2xl font-semibold">{loading ? "—" : pending}</div>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2">
            <Clock size={18} />
          </div>
        </div>
      </div>
    </section>
  );
}

