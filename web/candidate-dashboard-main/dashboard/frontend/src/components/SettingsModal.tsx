import { useEffect, useState } from "react";

type Props = {
  open: boolean;
  onClose: () => void;
};

export default function SettingsModal({ open, onClose }: Props) {
  const [dark, setDark] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "light") {
      setDark(false);
      document.documentElement.classList.remove("dark");
    } else {
      setDark(true);
      document.documentElement.classList.add("dark");
    }
  }, []);

  const toggleTheme = () => {
    const newDark = !dark;
    setDark(newDark);

    if (newDark) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl bg-slate-900 p-6 shadow-2xl border border-slate-800 text-white">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Настройки</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors text-2xl">
            ×
          </button>
        </div>

        <div className="flex items-center justify-between rounded-xl border border-slate-700 p-4 bg-slate-800/50">
          <div>
            <div className="font-medium text-slate-100">Тёмная тема</div>
            <div className="text-sm text-slate-400">
              Переключение интерфейса
            </div>
          </div>

          <button
            onClick={toggleTheme}
            className={`relative h-6 w-11 rounded-full transition-colors duration-200 ${
              dark ? "bg-blue-600" : "bg-slate-600"
            }`}
          >
            <span
              className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow-sm transition-all duration-200 ${
                dark ? "left-5" : "left-0.5"
              }`}
            />
          </button>
        </div>

        <button
          onClick={onClose}
          className="mt-6 w-full py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm font-medium transition-colors"
        >
          Закрыть
        </button>
      </div>
    </div>
  );
}