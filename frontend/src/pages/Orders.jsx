import { useState, useEffect } from 'react'
import axios from 'axios'
import { Search, ChevronLeft, ChevronRight, Calendar } from 'lucide-react'
import { USE_MOCK_DATA, API_BASE_URL } from '../config'

const Orders = () => {
  const [orders, setOrders] = useState([])
  const [apps, setApps] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [selectedApp, setSelectedApp] = useState('')
  const [status, setStatus] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const generateMockOrders = (count) => {
    const statuses = ['pending', 'completed', 'cancelled', 'refunded']
    const paymentMethods = ['wechat', 'alipay', 'credit_card']
    const productTypes = ['subscription', 'virtual_item', 'gift']
    
    return Array.from({ length: count }, (_, i) => ({
      id: i + 1 + (page - 1) * 20,
      app_id: 1,
      user_id: Math.floor(Math.random() * 100) + 1,
      order_no: `ORD${Date.now()}${String(Math.random()).substring(2, 6)}`,
      amount: Math.random() * 200 + 10,
      status: statuses[Math.floor(Math.random() * statuses.length)],
      payment_method: paymentMethods[Math.floor(Math.random() * paymentMethods.length)],
      product_type: productTypes[Math.floor(Math.random() * productTypes.length)],
      product_id: `prod_${Math.floor(Math.random() * 100)}`,
      created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString()
    }))
  }

  useEffect(() => {
    if (USE_MOCK_DATA) {
      setApps([
        { id: 1, name: 'ChatStar Live' },
        { id: 2, name: 'ChatStar Dating' },
        { id: 3, name: 'ChatStar Gaming' }
      ])
      setStats({
        total_orders: 500,
        completed_orders: 350,
        pending_orders: 80,
        cancelled_orders: 50,
        refunded_orders: 20,
        total_revenue: 25000
      })
    } else {
      fetchApps()
      fetchStats()
    }
  }, [selectedApp])

  useEffect(() => {
    if (USE_MOCK_DATA) {
      setLoading(true)
      setTimeout(() => {
        const mockOrders = generateMockOrders(20)
        let filteredOrders = mockOrders

        if (search) {
          filteredOrders = filteredOrders.filter(o => o.order_no.includes(search))
        }

        if (status) {
          filteredOrders = filteredOrders.filter(o => o.status === status)
        }

        setOrders(filteredOrders)
        setTotal(filteredOrders.length)
        setLoading(false)
      }, 300)
    } else {
      fetchOrders()
    }
  }, [page, search, selectedApp, status, startDate, endDate])

  const fetchApps = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/apps`)
      setApps(response.data.apps)
    } catch (error) {
      console.error('Failed to fetch apps:', error)
    }
  }

  const fetchStats = async () => {
    try {
      const params = selectedApp ? { app_id: selectedApp } : {}
      const response = await axios.get(`${API_BASE_URL}/api/orders/stats/summary`, { params })
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const fetchOrders = async () => {
    setLoading(true)
    try {
      const params = {
        page,
        per_page: 20,
        ...(search && { search }),
        ...(selectedApp && { app_id: selectedApp }),
        ...(status && { status }),
        ...(startDate && { start_date: startDate }),
        ...(endDate && { end_date: endDate }),
      }
      const response = await axios.get(`${API_BASE_URL}/api/orders`, { params })
      setOrders(response.data.orders)
      setTotal(response.data.total)
    } catch (error) {
      console.error('Failed to fetch orders:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    setSearch(e.target.value)
    setPage(1)
  }

  const updateOrderStatus = (orderId, newStatus) => {
    setOrders(orders.map(o => 
      o.id === orderId ? { ...o, status: newStatus } : o
    ))
    if (stats) {
      setStats({
        ...stats,
        completed_orders: newStatus === 'completed' ? stats.completed_orders + 1 : stats.completed_orders,
        pending_orders: newStatus === 'pending' ? stats.pending_orders + 1 : stats.pending_orders,
        cancelled_orders: newStatus === 'cancelled' ? stats.cancelled_orders + 1 : stats.cancelled_orders
      })
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-700'
      case 'pending':
        return 'bg-yellow-100 text-yellow-700'
      case 'cancelled':
        return 'bg-red-100 text-red-700'
      case 'refunded':
        return 'bg-gray-100 text-gray-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const getStatusLabel = (status) => {
    switch (status) {
      case 'completed':
        return '已完成'
      case 'pending':
        return '待处理'
      case 'cancelled':
        return '已取消'
      case 'refunded':
        return '已退款'
      default:
        return status
    }
  }

  return (
    <div className="space-y-6">
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-white rounded-xl shadow-sm border bborder-gray-200 p-6">
            <p className="text-sm text-gray-600 mb-1">总订单数</p>
            <p className="text-2xl font-bold text-gray-900">{stats.total_orders}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <p className="text-sm text-gray-600 mb-1">已完成</p>
            <p className="text-2xl font-bold text-green-600">{stats.completed_orders}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <p className="text-sm text-gray-600 mb-1">待处理</p>
            <p className="text-2xl font-bold text-yellow-600">{stats.pending_orders}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <p className="text-sm text-gray-600 mb-1">已取消</p>
            <p className="text-2xl font-bold text-red-600">{stats.cancelled_orders}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <p className="text-sm text-gray-600 mb-1">总收入</p>
            <p className="text-2xl font-bold text-primary-600">¥{stats.total_revenue.toFixed(2)}</p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              value={search}
              onChange={handleSearch}
              placeholder="搜索订单号"
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
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          >
            <option value="">所有状态</option>
            <option value="pending">待处理</option>
            <option value="completed">已完成</option>
            <option value="cancelled">已取消</option>
            <option value="refunded">已退款</option>
          </select>

          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
            />
          </div>

          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
            />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">订单号</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">用户ID</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">金额</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">状态</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">支付方式</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">产品类型</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">创建时间</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">操作</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="8" className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
                  </td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-8 text-gray-500">
                    暂无数据
                  </td>
                </tr>
              ) : (
                orders.map((order) => (
                  <tr key={order.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium text-gray-900">{order.order_no}</td>
                    <td className="py-3 px-4 text-gray-600">{order.user_id}</td>
                    <td className="py-3 px-4 text-gray-900 font-medium">¥{order.amount.toFixed(2)}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
                        {getStatusLabel(order.status)}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-600">{order.payment_method || '-'}</td>
                    <td className="py-3 px-4 text-gray-600">{order.product_type || '-'}</td>
                    <td className="py-3 px-4 text-gray-600 text-sm">
                      {new Date(order.created_at).toLocaleString('zh-CN')}
                    </td>
                    <td className="py-3 px-4">
                      {order.status === 'pending' && (
                        <div className="flex gap-2">
                          <button
                            onClick={() => updateOrderStatus(order.id, 'completed')}
                            className="px-3 py-1 bg-green-100 text-green-700 rounded-lg text-xs font-medium hover:bg-green-200 transition-colors"
                          >
                            完成
                          </button>
                          <button
                            onClick={() => updateOrderStatus(order.id, 'cancelled')}
                            className="px-3 py-1 bg-red-100 text-red-700 rounded-lg text-xs font-medium hover:bg-red-200 transition-colors"
                          >
                            取消
                          </button>
                        </div>
                      )}
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
                disabled={orders.length < 20}
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

export default Orders
