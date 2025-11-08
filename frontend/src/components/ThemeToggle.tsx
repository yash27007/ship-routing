import { useThemeStore } from '../stores/theme'
import { Sun, Moon } from 'lucide-react'

export default function ThemeToggle() {
    const { isDark, toggleTheme } = useThemeStore()

    return (
        <button
            onClick={toggleTheme}
            className="p-2 rounded-lg bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white hover:bg-slate-300 dark:hover:bg-slate-600 transition"
            aria-label="Toggle theme"
        >
            {isDark ? <Sun size={20} /> : <Moon size={20} />}
        </button>
    )
}
