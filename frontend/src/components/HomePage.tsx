'use client'

import { Store, MessageSquare, BarChart3, Package, MessageCircle, Zap, TrendingUp, Clock, Users, Target, MoreHorizontal, Calendar } from 'lucide-react'
import { LineChart, Line, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis } from 'recharts'
import { useState, useEffect } from 'react'

const trendData = [
  { name: 'Pzt', value: 8 },
  { name: 'Sal', value: 10 },
  { name: 'Çar', value: 7 },
  { name: 'Per', value: 12 },
  { name: 'Cum', value: 9 },
  { name: 'Cmt', value: 11 },
  { name: 'Paz', value: 12 },
]

const getPerformanceData = (themeColors) => [
  { name: 'Başarılı', value: 94.8, color: themeColors.primary },
  { name: 'Diğer', value: 5.2, color: '#E5E7EB' },
]

const usageData = [
  { name: 'Kullanıcılar', value: 2847 },
  { name: 'Oturumlar', value: 156 },
  { name: 'Dönüşüm', value: 24.6 },
]

// Sabit takvim verileri (SSR uyumlu)
const calendarData = [
  { date: '2025-01-09', day: 9, messages: 287, intensity: 3 },
  { date: '2025-01-10', day: 10, messages: 156, intensity: 2 },
  { date: '2025-01-11', day: 11, messages: 423, intensity: 4 },
  { date: '2025-01-12', day: 12, messages: 234, intensity: 2 },
  { date: '2025-01-13', day: 13, messages: 378, intensity: 3 },
  { date: '2025-01-14', day: 14, messages: 89, intensity: 1 },
  { date: '2025-01-15', day: 15, messages: 456, intensity: 4 },
  { date: '2025-01-16', day: 16, messages: 123, intensity: 1 },
  { date: '2025-01-17', day: 17, messages: 345, intensity: 3 },
  { date: '2025-01-18', day: 18, messages: 67, intensity: 1 },
  { date: '2025-01-19', day: 19, messages: 498, intensity: 4 },
  { date: '2025-01-20', day: 20, messages: 234, intensity: 2 },
  { date: '2025-01-21', day: 21, messages: 156, intensity: 2 },
  { date: '2025-01-22', day: 22, messages: 389, intensity: 3 },
  { date: '2025-01-23', day: 23, messages: 45, intensity: 1 },
  { date: '2025-01-24', day: 24, messages: 267, intensity: 3 },
  { date: '2025-01-25', day: 25, messages: 178, intensity: 2 },
  { date: '2025-01-26', day: 26, messages: 445, intensity: 4 },
  { date: '2025-01-27', day: 27, messages: 234, intensity: 2 },
  { date: '2025-01-28', day: 28, messages: 356, intensity: 3 },
  { date: '2025-01-29', day: 29, messages: 123, intensity: 1 },
  { date: '2025-01-30', day: 30, messages: 467, intensity: 4 },
  { date: '2025-01-31', day: 31, messages: 89, intensity: 1 },
  { date: '2025-02-01', day: 1, messages: 234, intensity: 2 },
  { date: '2025-02-02', day: 2, messages: 378, intensity: 3 },
  { date: '2025-02-03', day: 3, messages: 456, intensity: 4 },
  { date: '2025-02-04', day: 4, messages: 167, intensity: 2 },
  { date: '2025-02-05', day: 5, messages: 289, intensity: 3 },
  { date: '2025-02-06', day: 6, messages: 345, intensity: 3 },
  { date: '2025-02-07', day: 7, messages: 423, intensity: 4 }
]

export default function HomePage({ shouldExit, onAnimationComplete, isActive, themeColors }) {
  const [hoveredDay, setHoveredDay] = useState(null)
  const [isVisible, setIsVisible] = useState(false)
  const [isExiting, setIsExiting] = useState(false)
  
  // Theme renklerini kullanarak performans verisini oluştur
  const performanceData = getPerformanceData(themeColors)

  // Ana sayfaya döndüğünde state'leri sıfırla
  useEffect(() => {
    if (isActive && !shouldExit) {
      // State'leri sıfırla
      setIsVisible(false)
      setIsExiting(false)
      
      // Kartları sırayla göster
      const timer = setTimeout(() => {
        setIsVisible(true)
      }, 100)
      
      return () => clearTimeout(timer)
    }
  }, [isActive, shouldExit])

  useEffect(() => {
    if (shouldExit) {
      // Çıkış animasyonu başlat
      setIsExiting(true)
      const timer = setTimeout(() => {
        if (onAnimationComplete) {
          onAnimationComplete()
        }
      }, 1200) // Tüm kartların çıkması için yeterli süre
      
      return () => clearTimeout(timer)
    }
  }, [shouldExit, onAnimationComplete])
  
  const getIntensityColor = (intensity) => {
    const colors = [
      '#F0FDF4', // 0 - en açık yeşil (hiç etkileşim yok)
      '#DCFCE7', // 1 - açık yeşil
      '#BBF7D0', // 2 - orta açık yeşil
      '#4ADE80', // 3 - orta yeşil
      '#00AC78'  // 4 - en koyu yeşil (en çok etkileşim)
    ]
    return colors[intensity] || colors[0]
  }
  
  // Her kartın animasyon sınıfını belirle
  const getCardAnimation = (index) => {
    const baseClasses = "transition-all duration-700 ease-out"
    if (isExiting) {
      return `${baseClasses} opacity-0 translate-y-8 scale-95`
    }
    if (isVisible) {
      return `${baseClasses} opacity-100 translate-y-0 scale-100`
    }
    return `${baseClasses} opacity-0 translate-y-12 scale-90`
  }

  // Her kartın gecikme süresini belirle
  const getAnimationDelay = (index) => {
    if (isExiting) {
      return `${(6 - index) * 150}ms` // Çıkışta ters sırada (7 kart olduğu için)
    }
    return `${index * 150}ms` // Girişte sırayla
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4 sm:gap-6">
      
      {/* Store Info Card */}
      <div 
        className={`bg-white rounded-xl p-4 sm:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] hover:shadow-[0px_12px_32px_rgba(100,52,248,0.12)] hover:scale-105 group border border-transparent hover:border-[#6434F8]/20 lg:col-span-1 ${getCardAnimation(0)}`}
        style={{ animationDelay: getAnimationDelay(0) }}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div 
              className="w-12 h-12 rounded-xl flex items-center justify-center mr-3 shadow-lg"
              style={{ background: `linear-gradient(to bottom right, ${themeColors.primary}, ${themeColors.secondary})` }}
            >
              <Store className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-[#1F1F1F]">Mağaza</h3>
              <p className="text-base text-[#666]">Genel Durum</p>
            </div>
          </div>
          <MoreHorizontal className="w-5 h-5 text-[#666] opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" />
        </div>
        <div className="space-y-4">
          <div 
            className="p-3 rounded-lg flex items-center justify-between"
            style={{ background: `linear-gradient(to right, ${themeColors.primary}0D, ${themeColors.secondary}0D)` }}
          >
            <div>
              <p className="text-base font-medium" style={{ color: themeColors.primary }}>TechMall Store</p>
              <p className="text-sm text-[#666]">WooCommerce Platform</p>
            </div>
            <div className="flex items-center bg-green-50 px-3 py-2 rounded-full">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
              <span className="text-base text-green-600 font-semibold">Aktif Çalışıyor</span>
            </div>
          </div>
          <div 
            className="p-3 rounded-lg flex items-center justify-between"
            style={{ background: `linear-gradient(to right, ${themeColors.primary}0D, ${themeColors.secondary}0D)` }}
          >
            <div>
              <p className="text-base font-medium" style={{ color: themeColors.primary }}>Digital Market</p>
              <p className="text-sm text-[#666]">Magento Platform</p>
            </div>
            <div className="flex items-center bg-gray-50 px-3 py-2 rounded-full">
              <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
              <span className="text-base text-gray-600 font-semibold">Aktif Çalışmıyor</span>
            </div>
          </div>
        </div>
      </div>

      {/* Active Chatbox Card - 2 Sütun */}
      <div 
        className={`col-span-full lg:col-span-2 xl:col-span-2 bg-white rounded-xl p-4 sm:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] hover:shadow-[0px_12px_32px_rgba(100,52,248,0.12)] hover:scale-[1.02] group border border-transparent hover:border-[#6434F8]/20 ${getCardAnimation(1)}`}
        style={{ animationDelay: getAnimationDelay(1) }}
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <div 
              className="w-14 h-14 rounded-xl flex items-center justify-center mr-4 shadow-lg"
              style={{ background: `linear-gradient(to bottom right, ${themeColors.primary}, ${themeColors.secondary})` }}
            >
              <MessageSquare className="w-7 h-7 text-white" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-[#1F1F1F]">Aktif Chatbox&apos;lar</h3>
              <p className="text-base text-[#666]">Toplam etkileşim merkezi sayısı</p>
            </div>
          </div>
          <MoreHorizontal className="w-5 h-5 text-[#666] opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" />
        </div>
        
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="flex-1">
            <div className="flex flex-col sm:flex-row sm:items-end sm:space-x-2 mb-4">
              <div 
                className="text-5xl sm:text-6xl font-black bg-clip-text text-transparent"
                style={{ 
                  background: `linear-gradient(to right, ${themeColors.primary}, ${themeColors.secondary})`,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent'
                }}
              >12</div>
              <div className="flex items-center bg-green-50 px-3 py-1 rounded-full mt-2 sm:mt-0 sm:mb-2 w-fit">
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                <span className="text-green-600 font-bold">+8%</span>
                <span className="text-[#666] ml-1 text-base">bu hafta</span>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row sm:space-x-4 space-y-2 sm:space-y-0 text-base">
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: themeColors.primary }}></div>
                <span className="text-[#666]">Bu Hafta: 12</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-[#E5E7EB] rounded-full mr-2"></div>
                <span className="text-[#666]">Geçen Hafta: 11</span>
              </div>
            </div>
          </div>
          
          <div className="flex-1 h-20 sm:h-24 mt-4 lg:mt-0">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke={themeColors.primary}
                  strokeWidth={3}
                  dot={{ fill: themeColors.primary, strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: themeColors.primary, strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Chatbox Usage Statistics */}
      <div 
        className={`bg-white rounded-xl p-4 sm:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] hover:shadow-[0px_12px_32px_rgba(100,52,248,0.12)] hover:scale-105 group border border-transparent hover:border-[#6434F8]/20 lg:col-span-1 ${getCardAnimation(2)}`}
        style={{ animationDelay: getAnimationDelay(2) }}
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <div 
              className="w-12 h-12 rounded-xl flex items-center justify-center mr-3 shadow-lg"
              style={{ background: `linear-gradient(to bottom right, ${themeColors.primary}, ${themeColors.secondary})` }}
            >
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-[#1F1F1F]">İstatistikler</h3>
              <p className="text-base text-[#666]">Kullanım Metrikleri</p>
            </div>
          </div>
          <MoreHorizontal className="w-5 h-5 text-[#666] opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" />
        </div>
        
        <div className="space-y-4">
          <div 
            className="p-4 rounded-xl"
            style={{ background: `linear-gradient(to right, ${themeColors.primary}0D, ${themeColors.secondary}0D)` }}
          >
            <div className="flex justify-between items-center mb-2">
              <span className="text-base font-medium text-[#666]">Toplam Kullanıcı</span>
              <div className="text-2xl font-bold" style={{ color: themeColors.primary }}>2,847</div>
            </div>
            <div className="w-full bg-[#E5E7EB] rounded-full h-2">
              <div 
                className="h-2 rounded-full" 
                style={{
                  width: '85%',
                  background: `linear-gradient(to right, ${themeColors.primary}, ${themeColors.secondary})`
                }}
              ></div>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-3">
            <div className="text-center p-3 bg-[#F9F9FB] rounded-lg">
              <div className="text-xl font-bold text-[#1F1F1F]">156</div>
              <div className="text-sm text-[#666]">Aktif Oturum</div>
            </div>
            <div 
              className="text-center p-3 rounded-lg"
              style={{ background: `linear-gradient(to right, ${themeColors.primary}1A, ${themeColors.secondary}1A)` }}
            >
              <div className="text-xl font-bold" style={{ color: themeColors.primary }}>24.6%</div>
              <div className="text-sm text-[#666]">Dönüşüm Oranı</div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Performance - 2 Sütun */}
      <div 
        className={`col-span-full lg:col-span-2 xl:col-span-2 bg-white rounded-xl p-4 sm:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] hover:shadow-[0px_12px_32px_rgba(100,52,248,0.12)] hover:scale-[1.02] group border border-transparent hover:border-[#6434F8]/20 ${getCardAnimation(3)}`}
        style={{ animationDelay: getAnimationDelay(3) }}
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <div 
              className="w-14 h-14 rounded-xl flex items-center justify-center mr-4 shadow-lg"
              style={{ background: `linear-gradient(to bottom right, ${themeColors.primary}, ${themeColors.secondary})` }}
            >
              <Zap className="w-7 h-7 text-white" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-[#1F1F1F]">AI Performansı</h3>
              <p className="text-base text-[#666]">Sistem başarı metrikleri</p>
            </div>
          </div>
          <MoreHorizontal className="w-5 h-5 text-[#666] opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" />
        </div>
        
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-6 lg:space-y-0">
          <div className="flex-1 space-y-4 sm:space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <MessageSquare className="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3" style={{ color: themeColors.primary }} />
                <span className="text-sm sm:text-base font-medium text-[#666]">Toplam Mesaj</span>
              </div>
              <span className="text-xl sm:text-2xl font-bold" style={{ color: themeColors.primary }}>1,247</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Clock className="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3" style={{ color: themeColors.primary }} />
                <span className="text-sm sm:text-base font-medium text-[#666]">Avg. Yanıt Süresi</span>
              </div>
              <span className="text-xl sm:text-2xl font-bold" style={{ color: themeColors.primary }}>1.2s</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Target className="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3" style={{ color: themeColors.primary }} />
                <span className="text-sm sm:text-base font-medium text-[#666]">AI Eşleşme Skoru</span>
              </div>
              <span 
                className="text-xl sm:text-2xl font-bold bg-clip-text text-transparent"
                style={{ 
                  background: `linear-gradient(to right, ${themeColors.primary}, ${themeColors.secondary})`,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent'
                }}
              >94.8%</span>
            </div>
          </div>
          
          <div className="flex justify-center lg:flex-1 lg:justify-center mt-4 lg:mt-0">
            <div className="relative w-36 h-36 sm:w-40 sm:h-40">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={performanceData}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={70}
                    startAngle={90}
                    endAngle={450}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {performanceData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-lg sm:text-2xl font-bold" style={{ color: themeColors.primary }}>94.8%</div>
                  <div className="text-sm text-[#666]">Başarı</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Ürün Chatbox'ları */}
      <div 
        className={`bg-white rounded-xl p-4 sm:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] hover:shadow-[0px_12px_32px_rgba(100,52,248,0.12)] hover:scale-105 group border border-transparent hover:border-[#6434F8]/20 lg:col-span-1 ${getCardAnimation(4)}`}
        style={{ animationDelay: getAnimationDelay(4) }}
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <div 
              className="w-12 h-12 rounded-xl flex items-center justify-center mr-3 shadow-lg"
              style={{ background: `linear-gradient(to bottom right, ${themeColors.primary}, ${themeColors.secondary})` }}
            >
              <Package className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-[#1F1F1F]">Ürünler</h3>
              <p className="text-base text-[#666]">Chatbox Durumu</p>
            </div>
          </div>
          <MoreHorizontal className="w-5 h-5 text-[#666] opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" />
        </div>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-xl border border-green-200 cursor-pointer hover:shadow-md transition-all">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-400 rounded-full mr-3 animate-pulse"></div>
              <div>
                <span className="text-base font-semibold text-[#1F1F1F]">iPhone 15 Pro</span>
                <div className="text-sm text-green-600">Aktif • 2 dk önce</div>
              </div>
            </div>
            <div className="text-sm bg-green-200 text-green-800 px-2 py-1 rounded-full">Online</div>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-xl border border-green-200 cursor-pointer hover:shadow-md transition-all">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-400 rounded-full mr-3 animate-pulse"></div>
              <div>
                <span className="text-base font-semibold text-[#1F1F1F]">MacBook Air</span>
                <div className="text-sm text-green-600">Aktif • 5 dk önce</div>
              </div>
            </div>
            <div className="text-sm bg-green-200 text-green-800 px-2 py-1 rounded-full">Online</div>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl border border-gray-200 cursor-pointer hover:shadow-md transition-all">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-gray-400 rounded-full mr-3"></div>
              <div>
                <span className="text-base font-semibold text-[#1F1F1F]">AirPods Pro</span>
                <div className="text-sm text-gray-600">Pasif • 1 saat önce</div>
              </div>
            </div>
            <div className="text-sm bg-gray-200 text-gray-800 px-2 py-1 rounded-full">Offline</div>
          </div>
        </div>
      </div>

      {/* Mini Takvim / Günlük Aktivite */}
      <div 
        className={`bg-white rounded-xl p-4 sm:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] hover:shadow-[0px_12px_32px_rgba(100,52,248,0.12)] hover:scale-105 group border border-transparent hover:border-[#6434F8]/20 relative lg:col-span-1 ${getCardAnimation(5)}`}
        style={{ animationDelay: getAnimationDelay(5) }}
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <div 
              className="w-12 h-12 rounded-xl flex items-center justify-center mr-3 shadow-lg"
              style={{ background: `linear-gradient(to bottom right, ${themeColors.primary}, ${themeColors.secondary})` }}
            >
              <Calendar className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-[#1F1F1F]">Aktivite</h3>
              <p className="text-base text-[#666]">Son 30 Gün</p>
            </div>
          </div>
          <MoreHorizontal className="w-5 h-5 text-[#666] opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" />
        </div>
        
        {/* Heat Calendar Grid */}
        <div className="space-y-3">
          <div className="text-sm text-[#666] mb-2">Günlük mesaj aktivitesi</div>
          
          {/* Calendar Days Grid - 6x5 layout */}
          <div className="grid grid-cols-6 sm:grid-cols-10 gap-1">
            {calendarData.map((day, index) => (
              <div
                key={index}
                className="relative aspect-square rounded-sm cursor-pointer transition-all duration-200 hover:scale-110 hover:shadow-sm"
                style={{ backgroundColor: getIntensityColor(day.intensity) }}
                onMouseEnter={() => setHoveredDay(day)}
                onMouseLeave={() => setHoveredDay(null)}
              >
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-xs font-medium text-[#374151]">
                    {day.day}
                  </span>
                </div>
              </div>
            ))}
          </div>
          
          {/* Yoğunluk Göstergesi */}
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-[#F3F4F6]">
            <div className="text-sm text-[#666]">Az</div>
            <div className="flex space-x-1">
              {[0, 1, 2, 3, 4].map((level) => (
                <div
                  key={level}
                  className="w-3 h-3 rounded-sm"
                  style={{ backgroundColor: getIntensityColor(level) }}
                />
              ))}
            </div>
            <div className="text-sm text-[#666]">Çok</div>
          </div>
        </div>

        {/* Hover Tooltip */}
        {hoveredDay && (
          <div className="absolute top-4 right-4 bg-[#1F1F1F] text-white px-3 py-2 rounded-lg shadow-lg z-10 text-sm font-medium">
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4" />
              <span>
                {new Date(hoveredDay.date).toLocaleDateString('tr-TR', { 
                  day: 'numeric', 
                  month: 'long' 
                })}
              </span>
            </div>
            <div className="text-[#00AC78] font-bold mt-1">
              {hoveredDay.messages} mesaj
            </div>
          </div>
        )}
      </div>

      {/* Son Etkileşimler - 4 Sütun (Full Width) */}
      <div 
        className={`col-span-full bg-white rounded-xl p-4 sm:p-6 shadow-[0px_4px_12px_rgba(0,0,0,0.05)] hover:shadow-[0px_12px_32px_rgba(100,52,248,0.12)] hover:scale-[1.02] group border border-transparent hover:border-[#6434F8]/20 ${getCardAnimation(6)}`}
        style={{ animationDelay: getAnimationDelay(6) }}
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <div 
              className="w-12 h-12 rounded-xl flex items-center justify-center mr-3 shadow-lg"
              style={{ background: `linear-gradient(to bottom right, ${themeColors.primary}, ${themeColors.secondary})` }}
            >
              <MessageCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-[#1F1F1F]">Son Etkileşimler</h3>
              <p className="text-base text-[#666]">Gerçek zamanlı kullanıcı mesajları</p>
            </div>
          </div>
          <MoreHorizontal className="w-5 h-5 text-[#666] opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" />
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          <div 
            className="flex items-start space-x-3 p-4 rounded-xl cursor-pointer transition-all"
            style={{ 
              background: `linear-gradient(to right, ${themeColors.primary}0D, ${themeColors.secondary}0D)`,
              border: `1px solid ${themeColors.primary}1A`
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = `linear-gradient(to right, ${themeColors.primary}1A, ${themeColors.secondary}1A)`;
              e.currentTarget.style.borderColor = `${themeColors.primary}33`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = `linear-gradient(to right, ${themeColors.primary}0D, ${themeColors.secondary}0D)`;
              e.currentTarget.style.borderColor = `${themeColors.primary}1A`;
            }}
          >
            <div 
              className="w-10 h-10 rounded-full flex items-center justify-center shadow-md"
              style={{ background: `linear-gradient(to bottom right, ${themeColors.primary}, ${themeColors.secondary})` }}
            >
              <Users className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-base font-bold text-[#1F1F1F]">Ahmet K.</p>
              <p className="text-base text-[#666] mb-2">Bu ürünün garantisi kaç yıl?</p>
              <div className="flex items-center text-sm" style={{ color: themeColors.primary }}>
                <Package className="w-3 h-3 mr-1" />
                <span>iPhone 15 Pro • 3 dk önce</span>
              </div>
            </div>
          </div>
          
          <div 
            className="flex items-start space-x-3 p-4 rounded-xl cursor-pointer transition-all"
            style={{ 
              background: `linear-gradient(to right, ${themeColors.primary}0D, ${themeColors.secondary}0D)`,
              border: `1px solid ${themeColors.primary}1A`
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = `linear-gradient(to right, ${themeColors.primary}1A, ${themeColors.secondary}1A)`;
              e.currentTarget.style.borderColor = `${themeColors.primary}33`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = `linear-gradient(to right, ${themeColors.primary}0D, ${themeColors.secondary}0D)`;
              e.currentTarget.style.borderColor = `${themeColors.primary}1A`;
            }}
          >
            <div 
              className="w-10 h-10 rounded-full flex items-center justify-center shadow-md"
              style={{ background: `linear-gradient(to bottom right, ${themeColors.primary}, ${themeColors.secondary})` }}
            >
              <Users className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-base font-bold text-[#1F1F1F]">Zeynep Y.</p>
              <p className="text-base text-[#666] mb-2">Kargo ücreti ne kadar?</p>
              <div className="flex items-center text-sm" style={{ color: themeColors.primary }}>
                <Package className="w-3 h-3 mr-1" />
                <span>MacBook Air • 7 dk önce</span>
              </div>
            </div>
          </div>
          
          <div 
            className="flex items-start space-x-3 p-4 rounded-xl cursor-pointer transition-all"
            style={{ 
              background: `linear-gradient(to right, ${themeColors.primary}0D, ${themeColors.secondary}0D)`,
              border: `1px solid ${themeColors.primary}1A`
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = `linear-gradient(to right, ${themeColors.primary}1A, ${themeColors.secondary}1A)`;
              e.currentTarget.style.borderColor = `${themeColors.primary}33`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = `linear-gradient(to right, ${themeColors.primary}0D, ${themeColors.secondary}0D)`;
              e.currentTarget.style.borderColor = `${themeColors.primary}1A`;
            }}
          >
            <div 
              className="w-10 h-10 rounded-full flex items-center justify-center shadow-md"
              style={{ background: `linear-gradient(to bottom right, ${themeColors.primary}, ${themeColors.secondary})` }}
            >
              <Users className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-base font-bold text-[#1F1F1F]">Mehmet A.</p>
              <p className="text-base text-[#666] mb-2">Indirim var mı bu ürünün?</p>
              <div className="flex items-center text-sm" style={{ color: themeColors.primary }}>
                <Package className="w-3 h-3 mr-1" />
                <span>AirPods Pro • 15 dk önce</span>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  )
}