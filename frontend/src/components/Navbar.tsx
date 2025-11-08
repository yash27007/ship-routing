import { useAuthStore } from '../stores/auth'
import { LogOut } from 'lucide-react'
import ThemeToggle from './ThemeToggle'

export default function Navbar() {
    const { user, logout } = useAuthStore()

    return (
        <nav className="bg-white dark:bg-slate-800 shadow">
            <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Ship Routing Optimization</h1>
                <div className="flex items-center gap-4">
                    {user && <span className="text-slate-700 dark:text-slate-300">{user.email}</span>}
                    <ThemeToggle />
                    <button
                        onClick={logout}
                        className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
                    >
                        <LogOut size={18} />
                        Logout
                    </button>
                </div>
            </div>
        </nav>
    )
}
