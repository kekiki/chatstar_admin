import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'
import { USE_MOCK_DATA, API_BASE_URL } from '../config'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      checkAuth()
    } else {
      setLoading(false)
    }
  }, [token])

  const checkAuth = async () => {
    try {
      if (USE_MOCK_DATA) {
        // Mock authentication check
        const mockUser = {
          id: 1,
          username: 'admin',
          email: 'admin@chatstar.com',
          is_active: true,
          created_at: new Date().toISOString(),
          last_login: new Date().toISOString()
        }
        setUser(mockUser)
      } else {
        // Real API call
        const response = await axios.get(`${API_BASE_URL}/api/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        setUser(response.data.user)
      }
    } catch (error) {
      localStorage.removeItem('token')
      setToken(null)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    if (USE_MOCK_DATA) {
      // Mock login - accept any credentials
      const mockUser = {
        id: 1,
        username: username,
        email: `${username}@chatstar.com`,
        is_active: true,
        created_at: new Date().toISOString(),
        last_login: new Date().toISOString()
      }
      
      const mockToken = 'mock-jwt-token-' + Date.now()
      setToken(mockToken)
      localStorage.setItem('token', mockToken)
      setUser(mockUser)
      
      return {
        access_token: mockToken,
        token_type: 'bearer',
        user: mockUser
      }
    } else {
      // Real API call
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, { username, password })
      setToken(response.data.access_token)
      localStorage.setItem('token', response.data.access_token)
      setUser(response.data.user)
      return response.data
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
