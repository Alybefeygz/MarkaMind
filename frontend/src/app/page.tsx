'use client'

import Sidebar from '@/components/Sidebar'
import HomePage from '@/components/HomePage'
import ChatboxManagement from '@/components/ChatboxManagement'
import VirtualStore, { productList } from '@/components/VirtualStore'
import MessagingRecords from '@/components/MessagingRecords'
import Profile from '@/components/Profile'
import { Menu, ChevronDown, Plus, MessageSquare, LogOut, Save, ArrowLeft } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { DEFAULT_THEME } from '@/lib/theme'
import { createChatbox, getUserChatboxes, type ChatboxCreate, type ChatboxResponse } from '@/lib/api'

// Kullanıcının mağaza verileri - Backend'den yüklenecek (mock veriler kaldırıldı)
const initialStoreList = []

export default function Home() {
  const router = useRouter()
  const [pageTitle, setPageTitle] = useState({ bold: 'Ana', normal: 'Sayfa' })
  const [currentPage, setCurrentPage] = useState(0)
  const [nextPage, setNextPage] = useState(0)
  const [isAnimating, setIsAnimating] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  
  // Mağaza listesi state'i
  const [storeList, setStoreList] = useState(initialStoreList)

  // Sabit tema - TÜM sayfalar için (VirtualStore dahil)
  const themeColors = DEFAULT_THEME
  
  // Chatbox dropdown state
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [selectedChatbox, setSelectedChatbox] = useState<{ id?: string; name: string }>({ name: 'Chatbox Seçin' })
  
  // Chatbox tab state
  const [activeTab, setActiveTab] = useState('Önizleme')

  // Yeni Chatbox oluşturma state'i
  const [isCreatingNewChatbox, setIsCreatingNewChatbox] = useState(false)

  // Yeni chatbox verileri - tema renkleriyle uyumlu default değerler
  const [newChatboxData, setNewChatboxData] = useState({
    name: '',
    brand_id: '',
    chatbox_title: '',
    initial_message: '',
    placeholder_text: 'Mesajınızı yazın...',
    primary_color: themeColors.primary,           // Tema ana rengi
    ai_message_color: '#E5E7EB',                  // Açık gri (AI mesajları)
    user_message_color: themeColors.primary,      // Tema ana rengi (kullanıcı mesajları)
    ai_text_color: '#1F2937',                     // Koyu gri (AI mesaj metni)
    user_text_color: '#FFFFFF',                   // Beyaz (kullanıcı mesaj metni)
    button_primary_color: themeColors.primary,    // Tema ana rengi (buton)
    button_border_color: '#FFB380',               // Açık turuncu (çerçeve)
    button_icon_color: '#FFFFFF',                 // Beyaz (icon)
    avatar_url: null,
    animation_style: 'fade',
    language: 'tr',
    status: 'draft',
    selectedStores: [],
    selectedProducts: []
  })

  // Responsive state for tab positions
  const [isMobileView, setIsMobileView] = useState(false)
  
  const chatboxTabs = [
    'Önizleme',
    'Özelleştirme',
    'Veri Kaynakları',
    'Entegrasyonlar'
  ]

  // Yeni chatbox oluşturma için tab'lar (Önizleme hariç)
  const newChatboxTabs = [
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
  
  // Authentication check - redirect to login if not authenticated
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/login')
    }
  }, [router])

  // Logout function
  const handleLogout = () => {
    // Clear all auth data from localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_data')

    // Redirect to login page
    router.push('/login')
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

  // Backend'den çekilen chatbox listesi
  const [chatboxList, setChatboxList] = useState<ChatboxResponse[]>([])
  const [isLoadingChatboxes, setIsLoadingChatboxes] = useState(false)

  // Chatbox'ları backend'den yükle
  useEffect(() => {
    const loadChatboxes = async () => {
      const token = localStorage.getItem('access_token')
      if (!token) return

      setIsLoadingChatboxes(true)
      try {
        const response = await getUserChatboxes(1, 100) // İlk 100 chatbox
        setChatboxList(response.items)

        // İlk chatbox'ı seçili yap
        if (response.items.length > 0) {
          setSelectedChatbox({ id: response.items[0].id, name: response.items[0].name })
        }
      } catch (error) {
        console.error('Chatbox\'lar yüklenirken hata:', error)
      } finally {
        setIsLoadingChatboxes(false)
      }
    }

    loadChatboxes()
  }, [])

  // Menü öğelerini tanımla (Sidebar ile aynı)
  const menuItems = [
    { label: 'Ana Sayfa', title: { bold: 'Ana', normal: 'Sayfa' } },
    { label: 'Chatbox', title: { bold: 'Chatbox', normal: 'Yönetimi' } },
    { label: 'Mağaza', title: { bold: 'Sanal', normal: 'Mağaza' } },
    { label: 'Mesajlaşma', title: { bold: 'Mesajlaşma', normal: 'Kayıtları' } },
    { label: 'Profil', title: { bold: '', normal: 'Profil' } },
  ]

  const handlePageChange = (pageIndex) => {
    // Başlığı güncelle
    setPageTitle(menuItems[pageIndex].title)

    // Chatbox oluşturma modundan çıkış - state'leri tema renkleriyle sıfırla
    if (isCreatingNewChatbox) {
      setNewChatboxData({
        name: '',
        brand_id: '',
        chatbox_title: '',
        initial_message: '',
        placeholder_text: 'Mesajınızı yazın...',
        primary_color: themeColors.primary,
        ai_message_color: '#E5E7EB',
        user_message_color: themeColors.primary,
        ai_text_color: '#1F2937',
        user_text_color: '#FFFFFF',
        button_primary_color: themeColors.primary,
        button_border_color: '#FFB380',
        button_icon_color: '#FFFFFF',
        avatar_url: null,
        animation_style: 'fade',
        language: 'tr',
        status: 'draft',
        selectedStores: [],
        selectedProducts: []
      })
      setIsCreatingNewChatbox(false)
      setActiveTab('Önizleme') // Default tab'a dön
    }

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
      {/* Sidebar - Sabit tema kullan */}
      <Sidebar
        onTitleChange={setPageTitle}
        onPageChange={handlePageChange}
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
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

            {/* Logout Button - Only visible on Profile page */}
            {currentPage === 4 && (
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-3 sm:px-4 py-2 rounded-xl font-medium text-white transition-all duration-300 shadow-sm hover:shadow-md hover:scale-105"
                style={{
                  background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                }}
                title="Çıkış Yap"
              >
                <LogOut className="w-4 h-4" />
                <span className="text-sm hidden sm:inline">
                  Çıkış Yap
                </span>
              </button>
            )}
            
            {/* Chatbox Management Controls - başlık Chatbox Yönetimi olduğunda göster */}
            {pageTitle.bold === 'Chatbox' && pageTitle.normal === 'Yönetimi' && (
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
                    <MessageSquare className="w-3 sm:w-4 h-3 sm:h-4 flex-shrink-0" style={{ color: themeColors.primary }} />
                    <span className="text-xs sm:text-sm font-medium text-gray-700 truncate">{selectedChatbox.name}</span>
                  </div>
                  <ChevronDown className={`w-3 sm:w-4 h-3 sm:h-4 text-gray-500 flex-shrink-0 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
                </button>

                {/* Dropdown Menu */}
                {isDropdownOpen && pageTitle.bold === 'Chatbox' && (
                  <div className="absolute left-0 sm:right-0 mt-2 w-full sm:w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
                    {isLoadingChatboxes ? (
                      <div className="flex items-center justify-center p-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                      </div>
                    ) : chatboxList.length === 0 ? (
                      <div className="p-4 text-center text-sm text-gray-500">
                        Henüz chatbox oluşturulmamış
                      </div>
                    ) : (
                      chatboxList.map((chatbox) => (
                        <div
                          key={chatbox.id}
                          onClick={() => {
                            setSelectedChatbox({ id: chatbox.id, name: chatbox.name })
                            setIsDropdownOpen(false)
                          }}
                          className="flex items-center justify-between p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                        >
                          <div className="flex items-center space-x-2 flex-1 min-w-0">
                            <MessageSquare className="w-3 sm:w-4 h-3 sm:h-4 flex-shrink-0" style={{ color: themeColors.primary }} />
                            <div className="min-w-0">
                              <p className="text-xs sm:text-sm font-medium text-gray-900 truncate">{chatbox.name}</p>
                            </div>
                          </div>
                          <div className="flex items-center flex-shrink-0">
                            <div className={`w-1.5 sm:w-2 h-1.5 sm:h-2 rounded-full ${chatbox.status === 'active' ? 'bg-green-400' : 'bg-gray-400'}`}></div>
                            <span className={`ml-1 sm:ml-2 text-xs ${chatbox.status === 'active' ? 'text-green-600' : 'text-gray-500'}`}>
                              {chatbox.status === 'active' ? 'Aktif' : 'Pasif'}
                            </span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>

              {/* New Chatbox Button */}
              <button
                onClick={() => {
                  // State'i tema renkleriyle reset et
                  setNewChatboxData({
                    name: '',
                    brand_id: '',
                    chatbox_title: '',
                    initial_message: '',
                    placeholder_text: 'Mesajınızı yazın...',
                    primary_color: themeColors.primary,
                    ai_message_color: '#E5E7EB',
                    user_message_color: themeColors.primary,
                    ai_text_color: '#1F2937',
                    user_text_color: '#FFFFFF',
                    button_primary_color: themeColors.primary,
                    button_border_color: '#FFB380',
                    button_icon_color: '#FFFFFF',
                    avatar_url: null,
                    animation_style: 'fade',
                    language: 'tr',
                    status: 'draft',
                    selectedStores: [],
                    selectedProducts: []
                  })
                  setIsCreatingNewChatbox(true)
                  setActiveTab('Özelleştirme') // Tab'ı sıfırla
                  setPageTitle({ bold: 'Chatbox', normal: 'Oluşturma' }) // Başlığı güncelle
                }}
                className="flex items-center justify-center space-x-1 sm:space-x-2 text-white px-2 sm:px-3 lg:px-4 py-1.5 sm:py-2 rounded-lg hover:shadow-lg shadow-sm transition-all text-xs sm:text-sm lg:text-base font-medium whitespace-nowrap"
                style={{
                  background: `linear-gradient(to right, ${themeColors.primary}, ${themeColors.secondary})`
                }}
              >
                <Plus className="w-3 sm:w-4 h-3 sm:h-4" />
                <span className="hidden sm:inline">Yeni Chatbox</span>
                <span className="sm:hidden">Yeni</span>
              </button>
            </div>
            )}

            {/* Mesajlaşma Kayıtları Controls - başlık Mesajlaşma olduğunda göster */}
            {pageTitle.bold === 'Mesajlaşma' && (
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
                    <MessageSquare className="w-3 sm:w-4 h-3 sm:h-4 flex-shrink-0" style={{ color: themeColors.primary }} />
                    <span className="text-xs sm:text-sm font-medium text-gray-700 truncate">{selectedChatbox.name}</span>
                  </div>
                  <ChevronDown className={`w-3 sm:w-4 h-3 sm:h-4 text-gray-500 flex-shrink-0 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
                </button>

                {/* Dropdown Menu */}
                {isDropdownOpen && pageTitle.bold === 'Mesajlaşma' && (
                  <div className="absolute left-0 sm:right-0 mt-2 w-full sm:w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
                    {isLoadingChatboxes ? (
                      <div className="flex items-center justify-center p-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                      </div>
                    ) : chatboxList.length === 0 ? (
                      <div className="p-4 text-center text-sm text-gray-500">
                        Henüz chatbox oluşturulmamış
                      </div>
                    ) : (
                      chatboxList.map((chatbox) => (
                        <div
                          key={chatbox.id}
                          onClick={() => {
                            setSelectedChatbox({ id: chatbox.id, name: chatbox.name })
                            setIsDropdownOpen(false)
                          }}
                          className="flex items-center justify-between p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                        >
                          <div className="flex items-center space-x-2 flex-1 min-w-0">
                            <MessageSquare className="w-3 sm:w-4 h-3 sm:h-4 flex-shrink-0" style={{ color: themeColors.primary }} />
                            <div className="min-w-0">
                              <p className="text-xs sm:text-sm font-medium text-gray-900 truncate">{chatbox.name}</p>
                            </div>
                          </div>
                          <div className="flex items-center flex-shrink-0">
                            <div className={`w-1.5 sm:w-2 h-1.5 sm:h-2 rounded-full ${chatbox.status === 'active' ? 'bg-green-400' : 'bg-gray-400'}`}></div>
                            <span className={`ml-1 sm:ml-2 text-xs ${chatbox.status === 'active' ? 'text-green-600' : 'text-gray-500'}`}>
                              {chatbox.status === 'active' ? 'Aktif' : 'Pasif'}
                            </span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            </div>
            )}
          </div>
          
          {/* Chatbox Tab Menüsü - Chatbox Yönetimi sayfasında */}
          {pageTitle.bold === 'Chatbox' && pageTitle.normal === 'Yönetimi' && !isCreatingNewChatbox && (
            <div className="mt-4 sm:mt-6 mb-4 sm:mb-6">
              <div className="border-b border-gray-200 relative overflow-x-auto scrollbar-hide">
                <div className="flex items-center justify-between ml-1 sm:ml-2 lg:ml-6 xl:ml-14 pr-2 sm:pr-4 lg:pr-6 xl:pr-8">
                  <div className="flex items-center space-x-2 sm:space-x-4 lg:space-x-6 xl:space-x-8 min-w-max">
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

                  {/* Kaydet/Vazgeç Butonları - Sadece Özelleştirme sekmesinde */}
                  {activeTab === 'Özelleştirme' && (
                    <div id="chatbox-save-buttons-container" className="flex items-center space-x-2 sm:space-x-3 pb-2">
                      {/* Butonlar ChatboxPrivatization tarafından portal ile buraya render edilecek */}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Chatbox Tab Menüsü - Chatbox Oluşturma sayfasında (Önizleme hariç) */}
          {pageTitle.bold === 'Chatbox' && pageTitle.normal === 'Oluşturma' && (
            <div className="mt-4 sm:mt-6 mb-4 sm:mb-6">
              <div className="border-b border-gray-200 relative overflow-x-auto scrollbar-hide overflow-y-visible">
                <div className="flex items-center justify-between ml-1 sm:ml-2 lg:ml-6 xl:ml-14 mr-1 sm:mr-2 lg:mr-6 xl:mr-14 px-2 sm:px-0 py-1">
                  {/* Tab'lar */}
                  <div className="flex items-center space-x-2 sm:space-x-4 lg:space-x-6 xl:space-x-8 min-w-max">
                    {newChatboxTabs.map((tab, index) => (
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

                  {/* Butonlar */}
                  <div className="flex items-center space-x-2 sm:space-x-3">
                    {/* Vazgeç Butonu */}
                    <button
                      onClick={() => {
                        // State'i tema renkleriyle reset et
                        setNewChatboxData({
                          name: '',
                          brand_id: '',
                          chatbox_title: '',
                          initial_message: '',
                          placeholder_text: 'Mesajınızı yazın...',
                          primary_color: themeColors.primary,
                          ai_message_color: '#E5E7EB',
                          user_message_color: themeColors.primary,
                          ai_text_color: '#1F2937',
                          user_text_color: '#FFFFFF',
                          button_primary_color: themeColors.primary,
                          button_border_color: '#FFB380',
                          button_icon_color: '#FFFFFF',
                          avatar_url: null,
                          animation_style: 'fade',
                          language: 'tr',
                          status: 'draft',
                          selectedStores: [],
                          selectedProducts: []
                        })
                        setIsCreatingNewChatbox(false)
                        setActiveTab('Önizleme') // Default tab'a dön
                        setPageTitle({ bold: 'Chatbox', normal: 'Yönetimi' })
                      }}
                      className="flex items-center justify-center text-gray-600 hover:text-gray-800 p-1.5 sm:p-2 lg:p-2.5 rounded-lg sm:rounded-xl font-medium border border-gray-300 hover:border-gray-400 bg-white hover:bg-gray-50 transition-all duration-300 hover:scale-105"
                      title="Vazgeç"
                    >
                      <ArrowLeft className="w-4 sm:w-5 lg:w-6 h-4 sm:h-5 lg:h-6" />
                    </button>

                    {/* Kaydet Butonu */}
                    <button
                      onClick={async () => {
                        try {
                          // Validation
                          if (!newChatboxData.name) {
                            alert('Lütfen chatbox ismini girin')
                            return
                          }
                          if (!newChatboxData.brand_id) {
                            alert('Lütfen en az bir mağaza seçin')
                            return
                          }
                          if (!newChatboxData.chatbox_title) {
                            alert('Lütfen chatbox başlığını girin')
                            return
                          }
                          if (!newChatboxData.initial_message) {
                            alert('Lütfen başlangıç mesajını girin')
                            return
                          }

                          console.log('Chatbox kaydediliyor...', newChatboxData)

                          // Backend'e kaydet
                          const chatboxPayload: ChatboxCreate = {
                            brand_id: newChatboxData.brand_id,
                            name: newChatboxData.name,
                            chatbox_title: newChatboxData.chatbox_title,
                            initial_message: newChatboxData.initial_message,
                            placeholder_text: newChatboxData.placeholder_text,
                            primary_color: newChatboxData.primary_color,
                            ai_message_color: newChatboxData.ai_message_color,
                            user_message_color: newChatboxData.user_message_color,
                            ai_text_color: newChatboxData.ai_text_color,
                            user_text_color: newChatboxData.user_text_color,
                            button_primary_color: newChatboxData.button_primary_color,
                            button_border_color: newChatboxData.button_border_color,
                            button_icon_color: newChatboxData.button_icon_color,
                            avatar_url: newChatboxData.avatar_url,
                            animation_style: newChatboxData.animation_style,
                            language: newChatboxData.language,
                            status: newChatboxData.status
                          }

                          const result = await createChatbox(chatboxPayload)
                          console.log('Chatbox başarıyla kaydedildi:', result)

                          // TODO: Mağaza ve ürün ilişkilendirmeleri de yapılacak
                          // selectedStores ve selectedProducts kullanılarak

                          alert('Chatbox başarıyla oluşturuldu!')

                          // Chatbox listesini yeniden yükle
                          const response = await getUserChatboxes(1, 100)
                          setChatboxList(response.items)

                          // Yeni oluşturulan chatbox'ı seç
                          setSelectedChatbox({ id: result.id, name: result.name })

                          // Formu tema renkleriyle sıfırla ve geri dön
                          setNewChatboxData({
                            name: '',
                            brand_id: '',
                            chatbox_title: '',
                            initial_message: '',
                            placeholder_text: 'Mesajınızı yazın...',
                            primary_color: themeColors.primary,
                            ai_message_color: '#E5E7EB',
                            user_message_color: themeColors.primary,
                            ai_text_color: '#1F2937',
                            user_text_color: '#FFFFFF',
                            button_primary_color: themeColors.primary,
                            button_border_color: '#FFB380',
                            button_icon_color: '#FFFFFF',
                            avatar_url: null,
                            animation_style: 'fade',
                            language: 'tr',
                            status: 'draft',
                            selectedStores: [],
                            selectedProducts: []
                          })
                          setIsCreatingNewChatbox(false)
                          setPageTitle({ bold: 'Chatbox', normal: 'Yönetimi' })
                        } catch (error) {
                          console.error('Chatbox kaydedilemedi:', error)
                          alert('Chatbox kaydedilirken bir hata oluştu: ' + (error instanceof Error ? error.message : 'Bilinmeyen hata'))
                        }
                      }}
                      className="flex items-center space-x-1 sm:space-x-2 text-white px-3 sm:px-4 lg:px-6 py-1.5 sm:py-2 lg:py-2.5 rounded-lg sm:rounded-xl font-medium shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105 text-xs sm:text-sm lg:text-base"
                      style={{
                        background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                      }}
                    >
                      <Save className="w-3 sm:w-4 lg:w-5 h-3 sm:h-4 lg:h-5" />
                      <span>Kaydet</span>
                    </button>
                  </div>
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
              shouldExit={isAnimating}
              onAnimationComplete={handleAnimationComplete}
              isActive={currentPage === 0}
              themeColors={themeColors}
            />
          )}

          {/* Diğer Sayfalar */}
          {showOtherPage && (
            <>
              {currentPage === 1 && <ChatboxManagement selectedChatbox={selectedChatbox} activeTab={activeTab} themeColors={themeColors} storeList={storeList} productList={productList} isCreatingNew={isCreatingNewChatbox} onCancelCreate={() => {
                // State'i tema renkleriyle reset et
                setNewChatboxData({
                  name: '',
                  brand_id: '',
                  chatbox_title: '',
                  initial_message: '',
                  placeholder_text: 'Mesajınızı yazın...',
                  primary_color: themeColors.primary,
                  ai_message_color: '#E5E7EB',
                  user_message_color: themeColors.primary,
                  ai_text_color: '#1F2937',
                  user_text_color: '#FFFFFF',
                  button_primary_color: themeColors.primary,
                  button_border_color: '#FFB380',
                  button_icon_color: '#FFFFFF',
                  avatar_url: null,
                  animation_style: 'fade',
                  language: 'tr',
                  status: 'draft',
                  selectedStores: [],
                  selectedProducts: []
                })
                setIsCreatingNewChatbox(false)
                setPageTitle({ bold: 'Chatbox', normal: 'Yönetimi' }) // Başlığı geri döndür
              }} chatboxData={newChatboxData} setChatboxData={setNewChatboxData} />}
              {currentPage === 2 && <VirtualStore themeColors={themeColors} storeList={storeList} setStoreList={setStoreList} />}
              {currentPage === 3 && <MessagingRecords themeColors={themeColors} />}
              {currentPage === 4 && <Profile themeColors={themeColors} />}
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
