import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Users from './pages/Users'
import Streamers from './pages/Streamers'
import Orders from './pages/Orders'
import AppConfig from './pages/AppConfig'
import MainLayout from './components/MainLayout'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="users" element={<Users />} />
          <Route path="streamers" element={<Streamers />} />
          <Route path="orders" element={<Orders />} />
          <Route path="apps" element={<AppConfig />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default App
