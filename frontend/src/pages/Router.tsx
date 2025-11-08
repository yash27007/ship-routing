import { useAuthStore } from '../stores/auth'
import AuthForm from '../components/AuthForm'
import Navbar from '../components/Navbar'
import RouteManager from '../components/RouteManager'
import RouteResults from '../components/RouteResults'

export default function Router() {
    const { token } = useAuthStore()

    if (!token) {
        return <AuthForm />
    }

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
            <Navbar />
            <div className="max-w-7xl mx-auto px-4 py-8">
                <RouteManager />
                <RouteResults />
            </div>
        </div>
    )
}
