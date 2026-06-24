import { useState, useEffect } from 'react'
import axios from 'axios'
import { Search, ChevronLeft, ChevronRight, Trash2 } from 'lucide-react'

const Streamers = () => {
  const [streamers, setStreamers] = useState([])
  const [apps, setApps] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [selectedApp, setSelectedApp] = useState('')
  const [filterActive, setFilterActive] = useState(null)
  const [filterVerified, setFilterVerified] = useState(null)

  useEffect(() => {
    fetchApps()
  }, [])

  useEffect(() => {
    fetchStreamers()
  }, [page, search, selectedApp, filterActive, filterVerified])

  const fetchApps = async () => {
    try {
      const response = await axios.get('/api/apps')
      setApps(response.data.apps)
    } catch (error) {
      console.error('Failed to fetch apps:', error)
    }
  }

  const fetchStreamers = async () => {
    setLoading(true)
    try {
      const params = {
        page,
        per_page: 20,
        ...(search && { search }),
        ...(selectedApp && { app_id: selectedApp }),
        ...(filterActive !== null && { is_active: filterActive }),
        ...(filterVerified !== null && { is_verified: filterVerified }),
      }
      const response = await axios.get('/api/streamers', { params })
      setStreamers(response.data.streamers)
      setTotal(response.data.total)
    } catch (error) {
      console.error('Failed to fetch streamers:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    setSearch(e.target.value)
    setPage(1)
  }

  const handleDelete = async (streamerId) => {
    if (!confirm('确定要删除这个主播吗？')) return
    
    try {
      await axios.delete(`/api/streamers/${streamerId}`)
      fetchStreamers()
    } catch (error) {
      console.error('Failed to delete streamer:', error)
      alert('删除失败')
    }
  }

  const toggleStatus = async (streamer) => {
    try {
      await axios.put(`/api/streamers/${streamer.id}`, {
        is_active: !streamer.is_active
      })
      fetchStreamers()
    } catch (error) {
      console.error('Failed to update streamer:', error)
      alert('更新失败')
    }
  }

  const toggleVerified = async (streamer) => {
    try {
      await axios.put(`/api/streamers/${streamer.id}`, {
        is_verified: !streamer.is_verified
      })
      fetchStreamers()
    } catch (error) {
      console.error('Failed to update streamer:', error)
      alert('更新失败')
    }
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
              placeholder="搜索主播名或显示名称"
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
            value={filterVerified === null ? '' : filterVerified.toString()}
            onChange={(e) => setFilterVerified(e.target.value === '' ? null : e.target.value === 'true')}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          >
            <option value="">所有认证</option>
            <option value="true">已认证</option>
            <option value="false">未认证</option>
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
                <th className="text-left py-3 px-4 font-semibold text-gray-700">显示名称</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">粉丝数</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">总收入</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">状态</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">认证</th>
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
              ) : streamers.length === 0 ? (
                <tr>
                  <td colSpan="9" className="text-center py-8 text-gray-500">
                    暂无数据
                  </td>
                </tr>
              ) : (
                streamers.map((streamer) => (
                  <tr key={streamer.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 text-gray-600">{streamer.id}</td>
                    <td className="py-3 px-4 font-medium text-gray-900">{streamer.username}</td>
                    <td className="py-3 px-4 text-gray-600">{streamer.display_name || '-'}</td>
                    <td className="py-3 px-4 text-gray-900 font-medium">{streamer.follower_count.toLocaleString()}</td>
                    <td className="py-3 px-4 text-gray-900 font-medium">¥{streamer.total_earnings.toFixed(2)}</td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => toggleStatus(streamer)}
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          streamer.is_active 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-red-100 text-red-700'
                        }`}
                      >
                        {streamer.is_active ? '活跃' : '禁用'}
                      </button>
                    </td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => toggleVerified(streamer)}
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          streamer.is_verified 
                            ? 'bg-blue-100 text-blue-700' 
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {streamer.is_verified ? '已认证' : '未认证'}
                      </button>
                    </td>
                    <td className="py-3 px-4 text-gray-600 text-sm">
                      {new Date(streamer.created_at).toLocaleDateString('zh-CN')}
                    </td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => handleDelete(streamer.id)}
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
                disabled={streamers.length < 20}
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

export default Streamers
