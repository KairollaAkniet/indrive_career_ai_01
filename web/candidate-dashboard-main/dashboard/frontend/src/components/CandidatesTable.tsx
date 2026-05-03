import React from "react";
import { RefreshCw } from "lucide-react";
import type { Candidate } from "../api/types";

type Props = {
  candidates: Candidate[];
  loading?: boolean;
  error?: string | null;
  onRefresh: () => void;
};

function scoreBadge(score: number) {

  if (score > 80) {
    return "border-green-900/50 bg-green-900/20 text-green-200";
  }
  if (score < 50) {
    return "border-red-900/50 bg-red-900/20 text-red-200";
  }
  return "border-slate-700 bg-slate-900/40 text-slate-100";
}

function rowHighlight(score: number) {
  if (score > 80) return "bg-green-950/20";
  if (score < 50) return "bg-red-950/20";
  return "";
}

export default function CandidatesTable({
  candidates,
  loading,
  error,
  onRefresh,
}: Props) {
  return (
    <section className="mt-6 rounded-xl border border-slate-800 bg-slate-950/50 shadow-soft">
      {/* Шапка таблицы + кнопка обновления данных */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 px-5 py-4">
        <div>
          <div className="text-sm text-slate-400">Кандидаты</div>
          <div className="mt-1 text-lg font-semibold">Таблица заявок</div>
        </div>

        <button
          onClick={onRefresh}
          className="flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 hover:bg-slate-900"
          disabled={loading}
          type="button"
          title="Перезагрузить список кандидатов"
        >
          <RefreshCw size={16} />
          Обновить данные
        </button>
      </div>

      <div className="px-5 pb-4 pt-3">
        {error ? (
          <div className="rounded-lg border border-red-900/40 bg-red-900/20 px-4 py-3 text-sm text-red-100">
            {error}
          </div>
        ) : null}

        <div className="mt-3 overflow-auto rounded-lg border border-slate-800">
          <table className="min-w-full table-auto border-collapse">
            <thead className="sticky top-0 bg-slate-950">
              <tr className="text-left text-xs font-semibold text-slate-400">
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">user_id</th>
                <th className="px-4 py-3">Имя</th>
                <th className="px-4 py-3">ai_score</th>
                <th className="px-4 py-3">ai_summary</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-400">
                    Загрузка...
                  </td>
                </tr>
              ) : candidates.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-10 text-center text-slate-400">
                    Нет кандидатов. При первом запуске БД будет заполнена тестовыми данными.
                  </td>
                </tr>
              ) : (
                candidates.map((c) => (
                  <tr
                    key={c.id}
                    className={[
                      "border-t border-slate-800 text-sm",
                      rowHighlight(c.ai_score),
                    ].join(" ")}
                  >
                    <td className="px-4 py-3 text-slate-200">{c.id}</td>
                    <td className="px-4 py-3 text-slate-200">{c.user_id}</td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-slate-100">{c.full_name ?? "—"}</div>
                      <div className="mt-0.5 text-xs text-slate-400">
                        @{c.username ?? "unknown"}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={[
                          "inline-flex items-center justify-center rounded-full border px-3 py-1 text-xs font-semibold",
                          scoreBadge(c.ai_score),
                        ].join(" ")}
                      >
                        {c.ai_score}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="max-w-xl truncate text-slate-300" title={c.ai_summary ?? "—"}>
                        {c.ai_summary ?? "—"}
                      </div>
                      <div className="mt-1 max-w-xl truncate text-xs text-slate-500" title={c.answers_text}>
                        {c.answers_text}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

