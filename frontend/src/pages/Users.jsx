import { useState, useEffect } from 'react'
import axios from 'axios'
import { Search, ChevronLeft, ChevronRight, Trash2 } from 'lucide-react'
import { USE_MOCK_DATA, API_BASE_URL } from '../config'

const Users = () => {
  const [users, setUsers] = useState([])
  const [apps, setApps] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [selectedApp, setSelectedApp] = useState('')
  const [filterActive, setFilterActive] = useState(null)
  const [filterPremium, setFilterPremium] = useState(null)

  // Generate mock users
  const generateMockUsers = (count) => {
    return Array.from({ length: count }, (_, i) => ({
      id: i + 1 + (page - 1) * 20,
      username: `user_${i + 1}`,
      email: `user${i + 1}@example.com`,
      phone: `138${String(Math.random()).substring(2, 10)}`,
      is_active: Math.random() > 0.1,
      is_premium: Math.random() > 0.7,
      total_spent: Math.random() * 500,
      created_at: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString()
    }))
  }

  useEffect(() => {
    if (USE_MOCK_DATA) {
      // Mock apps
      setApps([
        { id: 1, name: 'ChatStar Live' },
        { id: 2, name: 'ChatStar Dating' },
        { id: 3, name: 'ChatStar Gaming' }
      ])
    } else {
      fetchApps()
    }
  }, [])

  useEffect(() => {
    if (USE_MOCK_DATA) {
      // Mock users
      setLoading(true)
      setTimeout(() => {
        const mockUsers = generateMockUsers(20)
        let filteredUsers = mockUsers

        if (search) {
          filteredUsers = filteredUsers.filter(u => 
            u.username.includes(search) || 
            u.email.includes(search) || 
            u.phone.includes(search)
          )
        }

        if (filterActive !== null) {
          filteredUsers = filteredUsers.filter(u => u.is_active === filterActive)
        }

        if (filterPremium !== null) {
          filteredUsers = filteredUsers.filter(u => u.is_premium === filterPremium)
        }

        setUsers(filteredUsers)
        setTotal(filteredUsers.length)
        setLoading(false)
      }, 300)
    } else {
      fetchUsers()
    }
  }, [page, search, selectedApp, filterActive, filterPremium])

  const fetchApps = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/apps`)
      setApps(response.data.apps)
    } catch (error) {
      console.error('Failed to fetch apps:', error)
    }
  }

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const params = {
        page,
        per_page: 20,
        ...(search && { search }),
        ...(selectedApp && { app_id: selectedApp }),
        ...(filterActive !== null && { is_active: filterActive }),
        ...(filterPremium !== null && { is_premium: filterPremium }),
      }
      const response = await axios.get(`${API_BASE_URL}/api/users`, { params })
      setUsers(response.data.users)
      setTotal(response.data.total)
    } catch (error) {
      console.error('Failed to fetch users:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    setSearch(e.target.value)
    setPage(1)
  }

  const handleDelete = (userId) => {
    if (!confirm('确定要删除这个用户吗？')) return
    setUsers(users.filter(u => u.id !== userId))
    setTotal(total - 1)
  }

  const toggleUserStatus = (user) => {
    setUsers(users.map(u => 
      u.id === user.id ? { ...u, is_active: !u.is_active } : u
    ))
  }

  const togglePremium = (user) => {
    setUsers(users.map(u => 
      u.id === user.id ? { ...u, is_premium: !u.is_premium } : u
    ))
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              value={search}
              onChange={handleSearch}
              placeholder="搜索用户名、邮箱或手机号"
              className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
            />
          </div>
          
          <select
            value={selectedApp}
            onChange={(e) => setSelectedApp(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          >
            <option value="">所有应用</option>
            {apps.map((app) => (
              <option key={app.id} value={app.id}>
                {app.name}
              </option>
            ))}
          </select>

          <select
            value={filterActive === null ? '' : filterActive.toString()}
            onChange={(e) => setFilterActive(e.target.value === '' ? null : e.target.value === 'true')}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          >
            <option value="">所有状态</option>
            <option value="true">活跃</option>
            <option value="false">禁用</option>
          </select>

          <select
            value={filterPremium === null ? '' : filterPremium.toString()}
            onChange={(e) => setFilterPremium(e.target.value === '' ? null : e.target.value === 'true')}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          >
            <option value="">所有会员</option>
            <option value="true">会员</option>
            <option value="false">普通用户</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">ID</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">用户名</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">邮箱</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">手机号</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">总消费</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">状态</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">会员</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">注册时间</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">操作</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="9" className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan="9" className="text-center py-8 text-gray-500">
                    暂无数据
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 text-gray-600">{user.id}</td>
                    <td className="py-3 px-4 font-medium text-gray-900">{user.username}</td>
                    <td className="py-3 px-4 text-gray-600">{user.email || '-'}</td>
                    <td className="py-3 px-4 text-gray-600">{user.phone || '-'}</td>
                    <td className="py-3 px-4 text-gray-900 font-medium">¥{user.total_spent.toFixed(2)}</td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => toggleUserStatus(user)}
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          user.is_active 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-red-100 text-red-700'
                        }`}
                      >
                        {user.is_active ? '活跃' : '禁用'}
                      </button>
                    </td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => togglePremium(user)}
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          user.is_premium 
                            ? 'bg-yellow-100 text-yellow-700' 
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {user.is_premium ? '会员' : '普通'}
                      </button>
                    </td>
                    <td className="py-3 px-4 text-gray-600 text-sm">
                      {new Date(user.created_at).toLocaleDateString('zh-CN')}
                    </td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => handleDelete(user.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {total > 0 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              共 {total} 条记录
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
              <span className="text-sm text-gray-600">
                第 {page} 页
              </span>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={users.length < 20}
                className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Users
