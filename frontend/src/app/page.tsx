'use client'

import Sidebar from '@/components/Sidebar'
import HomePage from '@/components/HomePage'
import ChatboxManagement from '@/components/ChatboxManagement'
import VirtualStore, { productList } from '@/components/VirtualStore'
import MessagingRecords from '@/components/MessagingRecords'
import { Menu, ChevronDown, Plus, MessageSquare, Copy, User, Store, Mail, Lock, Eye, EyeOff, RefreshCw, Save, AlertTriangle } from 'lucide-react'
import { useState, useRef, useEffect, useMemo } from 'react'

// Kullanıcının mağaza verileri - ana state olarak taşındı
const initialStoreList = [
  {
    id: 1,
    name: 'TechMall Store',
    logo: 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=100&h=100&fit=crop&crop=center',
    status: 'active',
    platform: 'İKAS',
    primaryColor: '#DCFB6D',
    secondaryColor: '#232228',
    textColor: '#FFFFFF'
  },
  {
    id: 2,
    name: 'Digital Market',
    logo: 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=100&h=100&fit=crop&crop=center',
    status: 'inactive',
    platform: 'İKAS',
    primaryColor: '#DCFB6D',
    secondaryColor: '#232228',
    textColor: '#FFFFFF'
  }
]

export default function Home() {
  const [pageTitle, setPageTitle] = useState({ bold: 'Ana', normal: 'Sayfa' })
  const [currentPage, setCurrentPage] = useState(0)
  const [nextPage, setNextPage] = useState(0)
  const [isAnimating, setIsAnimating] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  
  // Mağaza listesi state'i - dinamik tema için
  const [storeList, setStoreList] = useState(initialStoreList)
  
  // İlk mağazanın tema renklerini dinamik olarak al
  const themeColors = useMemo(() => ({
    primary: storeList[0]?.primaryColor || '#FF6925',
    secondary: storeList[0]?.secondaryColor || '#FFBF31',
    text: storeList[0]?.textColor || '#FFFFFF'
  }), [storeList])
  
  // Chatbox dropdown state
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [selectedChatbox, setSelectedChatbox] = useState(() => {
    // Lazy initialization - chatboxList henüz tanımlanmamış olabilir
    return null
  })
  
  // Chatbox tab state
  const [activeTab, setActiveTab] = useState('Önizleme')

  // Responsive state for tab positions
  const [isMobileView, setIsMobileView] = useState(false)

  // Password Management States
  const [isPasswordEditing, setIsPasswordEditing] = useState(false)
  const [passwordData, setPasswordData] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  const [showPasswords, setShowPasswords] = useState({
    oldPassword: false,
    newPassword: false,
    confirmPassword: false
  })
  const [passwordErrors, setPasswordErrors] = useState({
    newPassword: '',
    confirmPassword: '',
    general: ''
  })

  // Password validation functions
  const validatePassword = (field, value) => {
    let error = ''

    if (field === 'newPassword') {
      if (value.length > 0 && value.length < 8) {
        error = 'Şifre en az 8 karakter olmalıdır'
      } else if (value === passwordData.oldPassword && value.length > 0) {
        error = 'Yeni şifre eski şifre ile aynı olamaz'
      }
    }

    if (field === 'confirmPassword') {
      if (value.length > 0 && value !== passwordData.newPassword) {
        error = 'Şifreler eşleşmiyor'
      }
    }

    setPasswordErrors(prev => ({ ...prev, [field]: error }))
    return error === ''
  }

  const chatboxTabs = [
    'Önizleme',
    'Özelleştirme', 
    'Veri Kaynakları',
    'Entegrasyonlar'
  ]
  
  // Active tab'ın index'ini bul
  const activeTabIndex = chatboxTabs.indexOf(activeTab)
  
  // Tab merkez pozisyonları - responsive değerler
  const tabCenterPositions = {
    mobile: [68, 154, 240, 325],    // Küçük ekranlar için pozisyonlar
    desktop: [93, 210, 340, 469]   // Büyük ekranlar için pozisyonlar
  }
  
  // Responsive çizgi genişliği
  const getUnderlineWidth = () => {
    return isMobileView ? 60 : 80
  }
  
  // Çizgi pozisyonu - responsive merkezi tab'ın merkezine hizala
  const getUnderlinePosition = (index: number) => {
    const positions = isMobileView ? tabCenterPositions.mobile : tabCenterPositions.desktop
    const width = isMobileView ? 60 : 80
    return positions[index] - (width / 2)
  }
  
  // Window resize handler
  useEffect(() => {
    const handleResize = () => {
      setIsMobileView(window.innerWidth < 640)
    }
    
    // Set initial value
    if (typeof window !== 'undefined') {
      setIsMobileView(window.innerWidth < 640)
      window.addEventListener('resize', handleResize)
      
      return () => window.removeEventListener('resize', handleResize)
    }
  }, [])
  
  const [chatboxList, setChatboxList] = useState([
    {
      id: 1,
      name: 'TechMall AI Assistant',
      status: 'active',
      messages: 1247,
      storeId: 1, // TechMall Store
      colors: {
        primary: '#DCFB6D',
        aiMessage: '#F8FFF4',
        userMessage: '#DCFB6D',
        borderColor: '#DCFB6D',
        aiTextColor: '#232228',
        userTextColor: '#232228',
        buttonPrimary: '#DCFB6D'
      },
      dataSources: ['Teknik ürün katalogları', 'Elektronik rehberleri', 'Garanti bilgileri'],
      integration: {
        homepage: true,
        selectedProducts: [],
        platform: 'İKAS'
      }
    },
    {
      id: 2,
      name: 'Digital Market Bot',
      status: 'active',
      messages: 890,
      storeId: 2, // Digital Market
      colors: {
        primary: '#6F55FF',
        aiMessage: '#F4F3FF',
        userMessage: '#6F55FF',
        borderColor: '#6F55FF',
        aiTextColor: '#232228',
        userTextColor: '#FFFFFF',
        buttonPrimary: '#6F55FF'
      },
      dataSources: ['Dijital ürün bilgileri', 'Yazılım lisans bilgileri', 'Teknik destek'],
      integration: {
        homepage: false,
        selectedProducts: ['all'], // Tüm ürünler seçili
        platform: 'İKAS'
      }
    },
    {
      id: 3,
      name: 'Premium Support Chat',
      status: 'active',
      messages: 456,
      storeId: 2, // Digital Market
      colors: {
        primary: '#232228',
        aiMessage: '#F9FAFB',
        userMessage: '#232228',
        borderColor: '#E5E7EB',
        aiTextColor: '#374151',
        userTextColor: '#FFFFFF',
        buttonPrimary: '#232228'
      },
      dataSources: ['Genel müşteri hizmetleri', 'SSS dokümanları', 'İade politikası'],
      integration: {
        homepage: true,
        selectedProducts: [], // Hiç ürün seçilmemiş
        platform: 'Kendi Web Sitem'
      }
    }
  ])

  // selectedChatbox'ı initialize et
  useEffect(() => {
    if (!selectedChatbox && chatboxList.length > 0) {
      setSelectedChatbox(chatboxList[0])
    }
  }, [selectedChatbox])

  // Menü öğelerini tanımla (Sidebar ile aynı)
  const menuItems = [
    { label: 'Ana Sayfa', title: { bold: 'Ana', normal: 'Sayfa' } },
    { label: 'Chatbox', title: { bold: 'Chatbox', normal: 'Yönetimi' } },
    { label: 'Mağaza', title: { bold: 'Sanal', normal: 'Mağaza' } },
    { label: 'Mesajlaşma', title: { bold: 'Mesajlaşma', normal: 'Kayıtları' } },
    { label: 'İstatistik', title: { bold: 'Kullanıcı', normal: 'Profili' } },
    { label: 'Profil', title: { bold: '', normal: 'Profil' } },
  ]

  const handlePageChange = (pageIndex) => {
    // Başlığı güncelle
    setPageTitle(menuItems[pageIndex].title)
    
    if (currentPage === 0 && pageIndex !== 0) {
      // Ana sayfadan çıkışta animasyon başlat
      setNextPage(pageIndex)
      setIsAnimating(true)
    } else if (currentPage !== 0 && pageIndex === 0) {
      // Ana sayfaya dönüşte direkt geçiş (animasyon HomePage'de başlayacak)
      setCurrentPage(pageIndex)
      setIsAnimating(false) // Animasyon durumunu sıfırla
    } else {
      // Diğer sayfalar arasında direkt geçiş
      setCurrentPage(pageIndex)
      setIsAnimating(false) // Animasyon durumunu sıfırla
    }
  }

  const handleAnimationComplete = () => {
    setCurrentPage(nextPage)
    setIsAnimating(false)
    // Animasyon tamamlandığında başlığı da güncelle
    setPageTitle(menuItems[nextPage].title)
  }
  
  // Render koşulları
  const showHomePage = (currentPage === 0 || isAnimating)
  const showOtherPage = currentPage !== 0 && !isAnimating

  return (
    <div className="min-h-screen bg-[#F9F9FB] font-sans">
      {/* Sidebar */}
      <Sidebar
        onTitleChange={setPageTitle}
        onPageChange={handlePageChange}
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        currentPage={currentPage}
        themeColors={themeColors}
      />
      
      <div className="flex h-screen">
        {/* Dinamik sidebar alanı */}
        <div className={`transition-all duration-300 ease-in-out ${
          isSidebarOpen ? 'w-16 sm:w-20 md:w-24' : 'w-3 sm:w-4 md:w-6'
        }`}></div>
        
        <div className={`flex-1 p-3 sm:p-4 md:p-6 lg:p-8 overflow-y-auto overflow-x-hidden transition-all duration-300 ease-in-out ${
          isSidebarOpen ? 'ml-0.5 sm:ml-0.5 md:ml-1' : 'ml-0.5 sm:ml-0.5 md:ml-1'
        }`}>
          {/* Header */}
          <div className="flex flex-col space-y-3 sm:flex-row sm:items-center sm:space-y-0 mb-4 sm:mb-6 relative mt-4 sm:mt-2 md:mt-0">
            <div className="flex items-center flex-1">
              {/* Hamburger Menu Button - başlığın arkasından kayarak çıkıyor */}
              <button
                onClick={() => setIsSidebarOpen(true)}
                className={`p-1.5 sm:p-2 rounded-lg transition-all duration-300 group mr-2 sm:mr-3 md:mr-4 ${
                  isSidebarOpen ? 'opacity-0 translate-x-6 sm:translate-x-7 md:translate-x-8 pointer-events-none' : 'opacity-100 translate-x-0'
                }`}
                style={{ 
                  backgroundColor: `${themeColors.primary}10`
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = `${themeColors.primary}20`}
                onMouseLeave={(e) => e.target.style.backgroundColor = `${themeColors.primary}10`}
              >
                <Menu 
                  className="w-4 sm:w-5 md:w-6 h-4 sm:h-5 md:h-6 group-hover:scale-110 transition-transform" 
                  style={{ color: themeColors.primary }}
                />
              </button>
              
              <h1 className="text-lg sm:text-xl md:text-2xl lg:text-3xl tracking-wide">
                <span className="text-[#1F1F1F] font-bold">{pageTitle.bold} </span>
                <span className="text-[#666] font-normal">{pageTitle.normal}</span>
              </h1>
            </div>
            
            {/* Chatbox Management Controls - başlık Chatbox veya Mesajlaşma olduğunda göster */}
            {(pageTitle.bold === 'Chatbox' || pageTitle.bold === 'Mesajlaşma') && (
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-2 lg:space-x-4 w-full sm:w-auto">
              {/* Chatbox Dropdown */}
              <div className="relative w-full sm:w-auto">
                <button
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="flex items-center justify-between space-x-1 sm:space-x-2 bg-white border border-gray-200 rounded-lg px-2 sm:px-3 lg:px-4 py-1.5 sm:py-2 w-full sm:min-w-[160px] lg:min-w-[180px] xl:min-w-[200px] shadow-sm transition-colors text-xs sm:text-sm lg:text-base"
                  style={{ 
                    borderColor: isDropdownOpen ? `${themeColors.primary}30` : '#d1d5db'
                  }}
                  onMouseEnter={(e) => e.target.style.borderColor = `${themeColors.primary}30`}
                  onMouseLeave={(e) => e.target.style.borderColor = isDropdownOpen ? `${themeColors.primary}30` : '#d1d5db'}
                >
                  <div className="flex items-center space-x-1 sm:space-x-2 flex-1 min-w-0">
                    <MessageSquare className="w-3 sm:w-4 h-3 sm:h-4 flex-shrink-0" style={{ color: selectedChatbox?.colors?.primary || themeColors.primary }} />
                    <span className="text-xs sm:text-sm font-medium text-gray-700 truncate">{selectedChatbox?.name || 'Chatbox Seçin'}</span>
                  </div>
                  <ChevronDown className={`w-3 sm:w-4 h-3 sm:h-4 text-gray-500 flex-shrink-0 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
                </button>

                {/* Dropdown Menu */}
                {isDropdownOpen && (pageTitle.bold === 'Chatbox' || pageTitle.bold === 'Mesajlaşma') && (
                  <div className="absolute left-0 sm:right-0 mt-2 w-full sm:w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
                    {chatboxList.map((chatbox) => (
                      <div
                        key={chatbox.id}
                        onClick={() => {
                          setSelectedChatbox(chatbox)
                          setIsDropdownOpen(false)
                        }}
                        className={`flex items-center justify-between p-3 cursor-pointer border-b border-gray-100 last:border-b-0 transition-colors ${
                          selectedChatbox.id === chatbox.id
                            ? 'bg-gradient-to-r from-gray-50 to-gray-100'
                            : 'hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-center space-x-2 flex-1 min-w-0">
                          {/* Chatbox'ın kendi renginde icon */}
                          <MessageSquare
                            className="w-4 sm:w-5 h-4 sm:h-5 flex-shrink-0"
                            style={{ color: chatbox.colors?.primary || '#6B7280' }}
                          />
                          <div className="min-w-0">
                            <p className="text-xs sm:text-sm font-medium text-gray-900 truncate">{chatbox.name}</p>
                            <p className="text-xs text-gray-500 truncate">{chatbox.messages} mesaj</p>
                          </div>
                        </div>
                        <div className="flex items-center flex-shrink-0 space-x-2">
                          {/* Renk paleti önizlemesi */}
                          <div className="flex space-x-1">
                            <div
                              className="w-2 h-2 rounded-full border border-gray-200"
                              style={{ backgroundColor: chatbox.colors?.primary || '#6B7280' }}
                              title="Primary Color"
                            ></div>
                            <div
                              className="w-2 h-2 rounded-full border border-gray-200"
                              style={{ backgroundColor: chatbox.colors?.userMessage || '#6B7280' }}
                              title="User Message Color"
                            ></div>
                            <div
                              className="w-2 h-2 rounded-full border border-gray-200"
                              style={{ backgroundColor: chatbox.colors?.aiMessage || '#F3F4F6' }}
                              title="AI Message Color"
                            ></div>
                          </div>
                          {/* Durum göstergesi */}
                          <div className={`w-1.5 sm:w-2 h-1.5 sm:h-2 rounded-full ${chatbox.status === 'active' ? 'bg-green-400' : 'bg-gray-400'}`}></div>
                          <span className={`text-xs ${chatbox.status === 'active' ? 'text-green-600' : 'text-gray-500'}`}>
                            {chatbox.status === 'active' ? 'Aktif' : 'Pasif'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

            </div>
            )}
          </div>
          
          {/* Chatbox Tab Menüsü - sadece Chatbox sayfasında göster */}
          {pageTitle.bold === 'Chatbox' && (
            <div className="mt-4 sm:mt-6 mb-4 sm:mb-6">
              <div className="border-b border-gray-200 relative overflow-x-auto scrollbar-hide">
                <div className="flex items-center space-x-2 sm:space-x-4 lg:space-x-6 xl:space-x-8 ml-1 sm:ml-2 lg:ml-6 xl:ml-14 min-w-max px-2 sm:px-0">
                  {chatboxTabs.map((tab, index) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`pb-2 sm:pb-3 font-medium transition-colors duration-200 relative text-xs sm:text-sm lg:text-base whitespace-nowrap px-1 sm:px-2 ${
                        activeTab === tab
                          ? ''
                          : 'text-gray-500 hover:text-gray-700'
                      }`}
                      style={{
                        color: activeTab === tab ? themeColors.primary : undefined
                      }}
                    >
                      {tab}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Çizgi - Chatbox sayfası hariç tüm sayfalarda göster */}
          {pageTitle.bold !== 'Chatbox' && (
            <div 
              className="h-px bg-[#E0E0E0] mb-6 sm:mb-8"
              style={{marginLeft: '-16px', width: 'calc(100% + 32px)'}}
            ></div>
          )}
          
          {/* Sayfa İçerikleri */}
          {showHomePage && (
            <HomePage
              key={storeList.length} // storeList değişince yeniden render et
              shouldExit={isAnimating}
              onAnimationComplete={handleAnimationComplete}
              isActive={currentPage === 0}
              themeColors={themeColors}
              storeList={storeList}
              onPageChange={handlePageChange}
              chatboxList={chatboxList}
            />
          )}

          {/* Diğer Sayfalar */}
          {showOtherPage && (
            <>
              {currentPage === 1 && <ChatboxManagement activeTab={activeTab} themeColors={selectedChatbox?.colors || themeColors} storeList={storeList} productList={productList} selectedChatbox={selectedChatbox} chatboxList={chatboxList} setChatboxList={setChatboxList} />}
              {currentPage === 2 && <VirtualStore themeColors={themeColors} storeList={storeList} setStoreList={setStoreList} chatboxList={chatboxList} />}
              {currentPage === 3 && <MessagingRecords themeColors={selectedChatbox?.colors || themeColors} chatboxList={chatboxList} selectedChatbox={selectedChatbox} onChatboxSelect={setSelectedChatbox} />}
              {currentPage === 4 && (
                <div className="flex flex-col lg:flex-row gap-4 sm:gap-6">
                  {/* First Integration Card */}
                  <div className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out translate-y-0 scale-100 w-full lg:w-1/2 h-[70vh]" style={{ borderColor: '#E5E7EB', animationDelay: '150ms' }}>
                    <div className="flex items-center p-4 sm:p-6 lg:p-8 border-b border-gray-200">
                      <h3 className="text-xl sm:text-2xl lg:text-3xl">
                        <span
                          className="font-bold bg-gradient-to-r bg-clip-text text-transparent"
                          style={{
                            backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                          }}
                        >
                          Profil
                        </span>
                        <span
                          className="font-normal bg-gradient-to-r bg-clip-text text-transparent"
                          style={{
                            backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                          }}
                        >
                        </span>
                      </h3>
                    </div>
                    <div className="flex-1 p-4 sm:p-6 lg:p-8 flex flex-col">
                      {/* Kullanıcı Profil Bilgileri */}
                      <div className="flex flex-col items-center space-y-4 sm:space-y-6">

                        {/* Profil Fotoğrafı ve Kullanıcı Bilgileri - Yan Yana */}
                        <div className="flex items-center justify-center space-x-4 sm:space-x-6 w-full">
                          {/* Profil Fotoğrafı */}
                          <div className="relative flex-shrink-0">
                            <div
                              className="w-20 sm:w-24 md:w-28 h-20 sm:h-24 md:h-28 rounded-full flex items-center justify-center shadow-lg border-4 border-white"
                              style={{
                                background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                              }}
                            >
                              <User className="w-8 sm:w-10 md:w-12 h-8 sm:h-10 md:h-12 text-white" />
                            </div>
                            <div className="absolute -bottom-1 -right-1 w-6 sm:w-7 h-6 sm:h-7 bg-green-400 rounded-full border-3 border-white flex items-center justify-center">
                              <div className="w-2 h-2 bg-white rounded-full"></div>
                            </div>
                          </div>

                          {/* Nickname & Full Name */}
                          <div className="flex-1 space-y-1">
                            <h4 className="text-xl sm:text-2xl font-bold text-[#1F1F1F]">@TechGuru</h4>
                            <p className="text-base sm:text-lg text-[#666] font-medium">Ahmet Yılmaz</p>
                          </div>
                        </div>

                        {/* Kullanıcı Bilgileri */}
                        <div className="w-full space-y-3 sm:space-y-4">

                          {/* Email */}
                          <div
                            className="flex items-center space-x-3 p-3 sm:p-4 rounded-xl"
                            style={{ background: `linear-gradient(to right, ${themeColors.primary}0D, ${themeColors.secondary}0D)` }}
                          >
                            <Mail className="w-5 h-5 flex-shrink-0" style={{ color: themeColors.primary }} />
                            <div className="min-w-0 flex-1">
                              <p className="text-sm text-[#666] font-medium">E-posta</p>
                              <p className="text-base font-semibold text-[#1F1F1F] truncate">ahmet.yilmaz@example.com</p>
                            </div>
                          </div>

                          {/* Bağlantılı Mağazalar Başlık */}
                          <div className="pt-2 sm:pt-4">
                            <h5 className="text-lg font-bold text-[#1F1F1F] mb-3 flex items-center">
                              <Store className="w-5 h-5 mr-2" style={{ color: themeColors.primary }} />
                              Bağlantılı Mağazalar
                            </h5>

                            {/* Mağazalar Listesi */}
                            <div className="space-y-2 sm:space-y-3 max-h-40 overflow-y-auto">
                              <div
                                className="flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all hover:shadow-sm"
                                style={{ background: `linear-gradient(to right, ${themeColors.primary}0D, ${themeColors.secondary}0D)` }}
                                onMouseEnter={(e) => {
                                  e.currentTarget.style.background = `linear-gradient(to right, ${themeColors.primary}1A, ${themeColors.secondary}1A)`;
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.background = `linear-gradient(to right, ${themeColors.primary}0D, ${themeColors.secondary}0D)`;
                                }}
                              >
                                <div className="flex items-center space-x-3">
                                  <div
                                    className="w-8 h-8 rounded-lg flex items-center justify-center"
                                    style={{ background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})` }}
                                  >
                                    <Store className="w-4 h-4 text-white" />
                                  </div>
                                  <div>
                                    <p className="text-sm font-semibold text-[#1F1F1F]">TechMall Store</p>
                                    <p className="text-xs text-[#666]">WooCommerce</p>
                                  </div>
                                </div>
                                <div className="flex items-center bg-green-50 px-2 py-1 rounded-full">
                                  <div className="w-1.5 h-1.5 bg-green-400 rounded-full mr-1.5"></div>
                                  <span className="text-xs font-medium text-green-600">Aktif</span>
                                </div>
                              </div>

                              <div
                                className="flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all hover:shadow-sm"
                                style={{ background: `linear-gradient(to right, ${themeColors.primary}0D, ${themeColors.secondary}0D)` }}
                                onMouseEnter={(e) => {
                                  e.currentTarget.style.background = `linear-gradient(to right, ${themeColors.primary}1A, ${themeColors.secondary}1A)`;
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.background = `linear-gradient(to right, ${themeColors.primary}0D, ${themeColors.secondary}0D)`;
                                }}
                              >
                                <div className="flex items-center space-x-3">
                                  <div
                                    className="w-8 h-8 rounded-lg flex items-center justify-center"
                                    style={{ background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})` }}
                                  >
                                    <Store className="w-4 h-4 text-white" />
                                  </div>
                                  <div>
                                    <p className="text-sm font-semibold text-[#1F1F1F]">Digital Market</p>
                                    <p className="text-xs text-[#666]">Magento</p>
                                  </div>
                                </div>
                                <div className="flex items-center bg-gray-50 px-2 py-1 rounded-full">
                                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mr-1.5"></div>
                                  <span className="text-xs font-medium text-gray-600">Pasif</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Second Integration Card */}
                  <div className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out translate-y-0 scale-100 w-full lg:w-1/2 h-[70vh]" style={{ borderColor: '#E5E7EB', animationDelay: '300ms' }}>
                    <div className="flex items-center p-4 sm:p-6 lg:p-8 border-b border-gray-200">
                      <h3 className="text-xl sm:text-2xl lg:text-3xl">
                        <span
                          className="font-bold bg-gradient-to-r bg-clip-text text-transparent"
                          style={{
                            backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                          }}
                        >
                          Şifre
                        </span>
                        <span
                          className="font-normal bg-gradient-to-r bg-clip-text text-transparent"
                          style={{
                            backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                          }}
                        >
                          Yönetimi
                        </span>
                      </h3>
                    </div>
                    <div className="flex-1 p-4 sm:p-6 lg:p-8 flex flex-col">
                      {/* Password Management Form */}
                      <div className="space-y-4 sm:space-y-6 flex-1">

                        {/* Password Fields */}
                        <div className="space-y-4">

                          {/* Old Password */}
                          <div className="space-y-2">
                            <label className="text-sm font-medium text-[#666] flex items-center">
                              <Lock className="w-4 h-4 mr-2" style={{ color: themeColors.primary }} />
                              Mevcut Şifre
                            </label>
                            <div className="relative">
                              <input
                                type={showPasswords.oldPassword ? 'text' : 'password'}
                                value={passwordData.oldPassword}
                                onChange={(e) => setPasswordData({ ...passwordData, oldPassword: e.target.value })}
                                disabled={!isPasswordEditing}
                                className={`w-full px-4 py-3 rounded-xl border transition-all duration-300 focus:outline-none focus:ring-2 pr-12 text-gray-800 ${
                                  isPasswordEditing
                                    ? 'border-gray-200 focus:border-transparent focus:ring-2 bg-white placeholder-gray-400'
                                    : 'border-gray-100 bg-gray-50 text-gray-400 cursor-not-allowed placeholder-gray-300'
                                }`}
                                style={{
                                  focusRingColor: isPasswordEditing ? `${themeColors.primary}30` : undefined
                                }}
                                placeholder="Mevcut şifrenizi girin"
                              />
                              <button
                                type="button"
                                onClick={() => setShowPasswords({ ...showPasswords, oldPassword: !showPasswords.oldPassword })}
                                disabled={!isPasswordEditing}
                                className={`absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-md transition-colors ${
                                  isPasswordEditing
                                    ? 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                                    : 'text-gray-300 cursor-not-allowed'
                                }`}
                              >
                                {showPasswords.oldPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                              </button>
                            </div>
                          </div>

                          {/* New Password */}
                          <div className="space-y-2">
                            <label className="text-sm font-medium text-[#666] flex items-center">
                              <Lock className="w-4 h-4 mr-2" style={{ color: themeColors.primary }} />
                              Yeni Şifre
                            </label>
                            <div className="relative">
                              <input
                                type={showPasswords.newPassword ? 'text' : 'password'}
                                value={passwordData.newPassword}
                                onChange={(e) => {
                                  const newValue = e.target.value
                                  setPasswordData({ ...passwordData, newPassword: newValue })
                                  // Real-time validation
                                  if (isPasswordEditing) {
                                    setTimeout(() => validatePassword('newPassword', newValue), 100)
                                  }
                                }}
                                disabled={!isPasswordEditing}
                                className={`w-full px-4 py-3 rounded-xl border transition-all duration-300 focus:outline-none focus:ring-2 pr-12 text-gray-800 ${
                                  isPasswordEditing
                                    ? 'border-gray-200 focus:border-transparent focus:ring-2 bg-white placeholder-gray-400'
                                    : 'border-gray-100 bg-gray-50 text-gray-400 cursor-not-allowed placeholder-gray-300'
                                }`}
                                style={{
                                  focusRingColor: isPasswordEditing ? `${themeColors.primary}30` : undefined
                                }}
                                placeholder="Yeni şifrenizi girin"
                              />
                              <button
                                type="button"
                                onClick={() => setShowPasswords({ ...showPasswords, newPassword: !showPasswords.newPassword })}
                                disabled={!isPasswordEditing}
                                className={`absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-md transition-colors ${
                                  isPasswordEditing
                                    ? 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                                    : 'text-gray-300 cursor-not-allowed'
                                }`}
                              >
                                {showPasswords.newPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                              </button>
                            </div>
                            {/* Error Message for New Password */}
                            {passwordErrors.newPassword && (
                              <div className="flex items-center space-x-2 text-red-500 text-sm mt-1">
                                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                                <span>{passwordErrors.newPassword}</span>
                              </div>
                            )}
                          </div>

                          {/* Confirm New Password */}
                          <div className="space-y-2">
                            <label className="text-sm font-medium text-[#666] flex items-center">
                              <Lock className="w-4 h-4 mr-2" style={{ color: themeColors.primary }} />
                              Yeni Şifre Tekrar
                            </label>
                            <div className="relative">
                              <input
                                type={showPasswords.confirmPassword ? 'text' : 'password'}
                                value={passwordData.confirmPassword}
                                onChange={(e) => {
                                  const newValue = e.target.value
                                  setPasswordData({ ...passwordData, confirmPassword: newValue })
                                  // Real-time validation
                                  if (isPasswordEditing) {
                                    setTimeout(() => validatePassword('confirmPassword', newValue), 100)
                                  }
                                }}
                                disabled={!isPasswordEditing}
                                className={`w-full px-4 py-3 rounded-xl border transition-all duration-300 focus:outline-none focus:ring-2 pr-12 text-gray-800 ${
                                  isPasswordEditing
                                    ? 'border-gray-200 focus:border-transparent focus:ring-2 bg-white placeholder-gray-400'
                                    : 'border-gray-100 bg-gray-50 text-gray-400 cursor-not-allowed placeholder-gray-300'
                                }`}
                                style={{
                                  focusRingColor: isPasswordEditing ? `${themeColors.primary}30` : undefined
                                }}
                                placeholder="Yeni şifrenizi tekrar girin"
                              />
                              <button
                                type="button"
                                onClick={() => setShowPasswords({ ...showPasswords, confirmPassword: !showPasswords.confirmPassword })}
                                disabled={!isPasswordEditing}
                                className={`absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-md transition-colors ${
                                  isPasswordEditing
                                    ? 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                                    : 'text-gray-300 cursor-not-allowed'
                                }`}
                              >
                                {showPasswords.confirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                              </button>
                            </div>
                            {/* Error Message for Confirm Password */}
                            {passwordErrors.confirmPassword && (
                              <div className="flex items-center space-x-2 text-red-500 text-sm mt-1">
                                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                                <span>{passwordErrors.confirmPassword}</span>
                              </div>
                            )}
                          </div>

                        </div>

                        {/* Action Buttons */}
                        <div className="flex justify-end space-x-3 pt-4">
                          {/* Refresh Password Button */}
                          <button
                            onClick={() => {
                              setIsPasswordEditing(!isPasswordEditing)
                              if (!isPasswordEditing) {
                                // Reset form when enabling edit mode
                                setPasswordData({ oldPassword: '', newPassword: '', confirmPassword: '' })
                                setShowPasswords({ oldPassword: false, newPassword: false, confirmPassword: false })
                                setPasswordErrors({ newPassword: '', confirmPassword: '', general: '' })
                              }
                            }}
                            className="flex items-center space-x-2 px-4 py-2 border border-gray-200 text-[#666] rounded-lg font-medium transition-all duration-300 hover:border-gray-300 hover:shadow-sm"
                            onMouseEnter={(e) => {
                              e.currentTarget.style.borderColor = `${themeColors.primary}30`
                              e.currentTarget.style.color = themeColors.primary
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.borderColor = '#d1d5db'
                              e.currentTarget.style.color = '#666'
                            }}
                          >
                            <RefreshCw className={`w-4 h-4 ${isPasswordEditing ? 'rotate-180' : ''} transition-transform duration-300`} />
                            <span>{isPasswordEditing ? 'İptal Et' : 'Şifremi Yenile'}</span>
                          </button>

                          {/* Save Button */}
                          <button
                            onClick={() => {
                              // Handle password save logic here
                              console.log('Password saved:', passwordData)
                              setIsPasswordEditing(false)
                              setPasswordData({ oldPassword: '', newPassword: '', confirmPassword: '' })
                              setShowPasswords({ oldPassword: false, newPassword: false, confirmPassword: false })
                              setPasswordErrors({ newPassword: '', confirmPassword: '', general: '' })
                            }}
                            disabled={
                              !isPasswordEditing ||
                              !passwordData.oldPassword ||
                              !passwordData.newPassword ||
                              !passwordData.confirmPassword ||
                              passwordData.newPassword !== passwordData.confirmPassword ||
                              passwordData.newPassword.length < 8 ||
                              passwordData.newPassword === passwordData.oldPassword ||
                              passwordErrors.newPassword ||
                              passwordErrors.confirmPassword
                            }
                            className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                              isPasswordEditing &&
                              passwordData.oldPassword &&
                              passwordData.newPassword &&
                              passwordData.confirmPassword &&
                              passwordData.newPassword === passwordData.confirmPassword &&
                              passwordData.newPassword.length >= 8 &&
                              passwordData.newPassword !== passwordData.oldPassword &&
                              !passwordErrors.newPassword &&
                              !passwordErrors.confirmPassword
                                ? 'text-white shadow-sm hover:shadow-md hover:scale-105'
                                : 'text-gray-400 bg-gray-100 cursor-not-allowed'
                            }`}
                            style={{
                              background: isPasswordEditing &&
                                       passwordData.oldPassword &&
                                       passwordData.newPassword &&
                                       passwordData.confirmPassword &&
                                       passwordData.newPassword === passwordData.confirmPassword &&
                                       passwordData.newPassword.length >= 8 &&
                                       passwordData.newPassword !== passwordData.oldPassword &&
                                       !passwordErrors.newPassword &&
                                       !passwordErrors.confirmPassword
                                ? `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                                : undefined
                            }}
                          >
                            <Save className="w-4 h-4" />
                            <span>Kaydet</span>
                          </button>
                        </div>

                      </div>
                    </div>
                  </div>
                </div>
              )}
              {currentPage !== 1 && currentPage !== 2 && currentPage !== 3 && currentPage !== 4 && (
                <div className="flex items-center justify-center h-96">
                  <div className="text-center text-[#666]">
                    <p>Bu sayfa henüz geliştirilmedi.</p>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
