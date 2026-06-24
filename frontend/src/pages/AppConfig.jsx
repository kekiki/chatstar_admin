import { useState, useEffect } from 'react'
import axios from 'axios'
import { Plus, Edit, Trash2, Key, Copy, Check } from 'lucide-react'
import { USE_MOCK_DATA, API_BASE_URL } from '../config'

const AppConfig = () => {
  const [apps, setApps] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingApp, setEditingApp] = useState(null)
  const [copiedKey, setCopiedKey] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    icon_url: '',
    config: '{}'
  })

  const generateMockApps = () => {
    return [
      {
        id: 1,
        name: 'ChatStar Live',
        description: '直播社交平台',
        icon_url: '',
        app_key: 'mock-key-live-' + Math.random().toString(36).substring(7),
        is_active: true,
        config: { max_users: 10000, features: ['chat', 'video', 'voice'] },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 2,
        name: 'ChatStar Dating',
        description: '交友约会平台',
        icon_url: '',
        app_key: 'mock-key-dating-' + Math.random().toString(36).substring(7),
        is_active: true,
        config: { max_users: 5000, features: ['chat', 'match'] },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 3,
        name: 'ChatStar Gaming',
        description: '游戏互动平台',
        icon_url: '',
        app_key: 'mock-key-gaming-' + Math.random().toString(36).substring(7),
        is_active: true,
        config: { max_users: 20000, features: ['chat', 'game', 'voice'] },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ]
  }

  useEffect(() => {
    if (USE_MOCK_DATA) {
      setLoading(true)
      setTimeout(() => {
        setApps(generateMockApps())
        setLoading(false)
      }, 300)
    } else {
      fetchApps()
    }
  }, [])

  const fetchApps = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE_URL}/api/apps`)
      setApps(response.data.apps)
    } catch (error) {
      console.error('Failed to fetch apps:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingApp(null)
    setFormData({
      name: '',
      description: '',
      icon_url: '',
      config: '{}'
    })
    setShowModal(true)
  }

  const handleEdit = (app) => {
    setEditingApp(app)
    setFormData({
      name: app.name,
      description: app.description || '',
      icon_url: app.icon_url || '',
      config: JSON.stringify(app.config || {}, null, 2)
    })
    setShowModal(true)
  }

  const handleDelete = (appId) => {
    if (!confirm('确定要删除这个应用吗？此操作不可恢复！')) return
    setApps(apps.filter(a => a.id !== appId))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    try {
      const config = JSON.parse(formData.config)
      
      if (editingApp) {
        setApps(apps.map(a => 
          a.id === editingApp.id 
            ? { ...a, name: formData.name, description: formData.description, icon_url: formData.icon_url, config, updated_at: new Date().toISOString() }
            : a
        ))
      } else {
        const newApp = {
          id: Math.max(...apps.map(a => a.id), 0) + 1,
          name: formData.name,
          description: formData.description,
          icon_url: formData.icon_url,
          app_key: 'mock-key-' + Math.random().toString(36).substring(7),
          is_active: true,
          config,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        setApps([...apps, newApp])
      }

      setShowModal(false)
    } catch (error) {
      alert('保存失败，请检查配置格式')
    }
  }

  const handleRegenerateKey = (appId) => {
    if (!confirm('确定要重新生成应用密钥吗？旧密钥将立即失效！')) return
    setApps(apps.map(a => 
      a.id === appId 
        ? { ...a, app_key: 'mock-key-' + Math.random().toString(36).substring(7), updated_at: new Date().toISOString() }
        : a
    ))
    alert('密钥已重新生成')
  }

  const copyToClipboard = (text, appId) => {
    navigator.clipboard.writeText(text)
    setCopiedKey(appId)
    setTimeout(() => setCopiedKey(null), 2000)
  }

  const toggleAppStatus = (app) => {
    setApps(apps.map(a => 
      a.id === app.id ? { ...a, is_active: !a.is_active } : a
    ))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">应用配置</h2>
        <button
          onClick={handleCreate}
          className="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center gap-2"
        >
          <Plus className="h-5 w-5" />
          新建应用
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : apps.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 text-center py-12">
          <p className="text-gray-500 mb-4">暂无应用</p>
          <button
            onClick={handleCreate}
            className="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
          >
            创建第一个应用
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {apps.map((app) => (
            <div key={app.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  {app.icon_url ? (
                    <img src={app.icon_url} alt={app.name} className="w-12 h-12 rounded-lg object-cover" />
                  ) : (
                    <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                      <span className="text-primary-600 font-bold text-xl">
                        {app.name[0]?.toUpperCase()}
                      </span>
                    </div>
                  )}
                  <div>
                    <h3 className="font-semibold text-gray-900">{app.name}</h3>
                    <p className="text-sm text-gray-500">ID: {app.id}</p>
                  </div>
                </div>
                <button
                  onClick={() => toggleAppStatus(app)}
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    app.is_active 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {app.is_active ? '启用' : '禁用'}
                </button>
              </div>

              <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                {app.description || '暂无描述'}
              </p>

              <div className="bg-gray-50 rounded-lg p-3 mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-500">应用密钥</span>
                  <button
                    onClick={() => copyToClipboard(app.app_key, app.id)}
                    className="text-primary-600 hover:text-primary-700"
                  >
                    {copiedKey === app.id ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </button>
                </div>
                <code className="text-xs text-gray-700 break-all">
                  {app.app_key}
                </code>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleEdit(app)}
                  className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 transition-colors"
                >
                  <Edit className="h-4 w-4" />
                  编辑
                </button>
                <button
                  onClick={() => handleRegenerateKey(app.id)}
                  className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 transition-colors"
                >
                  <Key className="h-4 w-4" />
                  重置密钥
                </button>
                <button
                  onClick={() => handleDelete(app.id)}
                  className="p-2 bg-red-100 hover:bg-red-200 rounded-lg text-red-600 transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-xl font-semibold text-gray-900">
                {editingApp ? '编辑应用' : '新建应用'}
              </h3>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  应用名称 *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  描述
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  图标URL
                </label>
                <input
                  type="url"
                  value={formData.icon_url}
                  onChange={(e) => setFormData({ ...formData, icon_url: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                  placeholder="https://example.com/icon.png"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  配置 (JSON)
                </label>
                <textarea
                  value={formData.config}
                  onChange={(e) => setFormData({ ...formData, config: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none font-mono text-sm"
                  rows={6}
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors duration-200"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
                >
                  {editingApp ? '保存' : '创建'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default AppConfig
