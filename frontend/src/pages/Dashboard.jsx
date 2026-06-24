import { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts'
import { 
  TrendingUp, 
  Users, 
  DollarSign, 
  Activity,
  ArrowUpRight
} from 'lucide-react'

const Dashboard = () => {
  const [selectedApp, setSelectedApp] = useState(null)
  const [apps, setApps] = useState([])
  const [stats, setStats] = useState(null)
  const [appStats, setAppStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchApps()
    fetchStats()
  }, [])

  useEffect(() => {
    if (selectedApp) {
      fetchAppStats(selectedApp)
    }
  }, [selectedApp])

  const fetchApps = async () => {
    try {
      const response = await axios.get('/api/dashboard/apps')
      setApps(response.data.apps)
      if (response.data.apps.length > 0) {
        setSelectedApp(response.data.apps[0].id)
      }
    } catch (error) {
      console.error('Failed to fetch apps:', error)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/dashboard/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const fetchAppStats = async (appId) => {
    setLoading(true)
    try {
      const response = await axios.get(`/api/dashboard/app/${appId}/stats`)
      setAppStats(response.data)
    } catch (error) {
      console.error('Failed to fetch app stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const StatCard = ({ title, value, icon: Icon, trendValue }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {trendValue && (
            <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
              <ArrowUpRight className="h-4 w-4" />
              {trendValue}
            </div>
          )}
        </div>
        <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
          <Icon className="h-6 w-6 text-primary-600" />
        </div>
      </div>
    </div>
  )

  if (loading && !appStats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <label className="text-sm font-medium text-gray-700">选择应用:</label>
        <select
          value={selectedApp || ''}
          onChange={(e) => setSelectedApp(Number(e.target.value))}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none max-w-xs"
        >
          {apps.map((app) => (
            <option key={app.id} value={app.id}>
              {app.name}
            </option>
          ))}
        </select>
      </div>

      {appStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="新增用户"
            value={appStats.summary.new_users}
            icon={Users}
            trendValue="本月"
          />
          <StatCard
            title="日活用户"
            value={appStats.summary.dau}
            icon={Activity}
            trendValue="今日"
          />
          <StatCard
            title="新增付费"
            value={`¥${appStats.summary.new_payment_amount.toFixed(2)}`}
            icon={DollarSign}
            trendValue="本月"
          />
          <StatCard
            title="总付费"
            value={`¥${appStats.summary.total_payment_amount.toFixed(2)}`}
            icon={TrendingUp}
            trendValue="累计"
          />
        </div>
      )}

      {appStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">新增付费率</h3>
            <div className="flex items-center gap-4">
              <div className="text-4xl font-bold text-primary-600">
                {appStats.summary.new_payment_rate}%
              </div>
              <p className="text-gray-600">
                本月新增用户中付费比例
              </p>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">日活付费率</h3>
            <div className="flex items-center gap-4">
              <div className="text-4xl font-bold text-primary-600">
                {appStats.summary.dau_payment_rate}%
              </div>
              <p className="text-gray-600">
                今日活跃用户中付费比例
              </p>
            </div>
          </div>
        </div>
      )}

      {appStats && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">新增用户趋势</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={appStats.daily_stats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString('zh-CN')}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="new_users" 
                  stroke="#0ea5e9" 
                  name="新增用户"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">付费金额趋势</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={appStats.daily_stats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date"
                  tickFormatter={(value) => new Date(value).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString('zh-CN')}
                  formatter={(value) => [`¥${value.toFixed(2)}`, '付费金额']}
                />
                <Legend />
                <Bar 
                  dataKey="new_payment_amount" 
                  fill="#0ea5e9" 
                  name="付费金额"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">日活用户趋势</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={appStats.daily_stats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date"
                  tickFormatter={(value) => new Date(value).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString('zh-CN')}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="dau" 
                  stroke="#10b981" 
                  name="日活用户"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">用户与付费对比</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={appStats.daily_stats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date"
                  tickFormatter={(value) => new Date(value).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
                />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString('zh-CN')}
                />
                <Legend />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="new_users" 
                  stroke="#0ea5e9" 
                  name="新增用户"
                  strokeWidth={2}
                />
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="dau" 
                  stroke="#10b981" 
                  name="日活用户"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
