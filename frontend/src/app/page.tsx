'use client'

import Sidebar from '@/components/Sidebar'
import HomePage from '@/components/HomePage'
import ChatboxManagement from '@/components/ChatboxManagement'
import VirtualStore from '@/components/VirtualStore'
import { Menu, ChevronDown, Plus, MessageSquare } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'

// Kullanıcının mağaza verileri - ana state olarak taşındı
const initialStoreList = [
  { 
    id: 1, 
    name: 'TechMall Store', 
    logo: 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=100&h=100&fit=crop&crop=center',
    status: 'active',
    platform: 'Trendyol',
    primaryColor: '#FF6925',
    secondaryColor: '#FFBF31',
    textColor: '#FFFFFF'
  },
  { 
    id: 2, 
    name: 'Digital Market', 
    logo: 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=100&h=100&fit=crop&crop=center',
    status: 'inactive',
    platform: 'Amazon',
    primaryColor: '#232F3E',
    secondaryColor: '#FF9900',
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
  const themeColors = {
    primary: storeList[0]?.primaryColor || '#FF6925',
    secondary: storeList[0]?.secondaryColor || '#FFBF31',
    text: storeList[0]?.textColor || '#FFFFFF'
  }
  
  // Chatbox dropdown state
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [selectedChatbox, setSelectedChatbox] = useState({ name: 'Zzen Chatbox' })
  
  // Chatbox tab state
  const [activeTab, setActiveTab] = useState('Önizleme')
  
  // Responsive state for tab positions
  const [isMobileView, setIsMobileView] = useState(false)
  
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
  
  const chatboxList = [
    { id: 1, name: 'Zzen Chatbox', status: 'active', messages: 1247 },
    { id: 2, name: 'Imuntus Kids Chatbox', status: 'active', messages: 890 },
    { id: 3, name: 'Mag4ever Chatbox', status: 'inactive', messages: 456 }
  ]

  // Menü öğelerini tanımla (Sidebar ile aynı)
  const menuItems = [
    { label: 'Ana Sayfa', title: { bold: 'Ana', normal: 'Sayfa' } },
    { label: 'Chatbox', title: { bold: 'Chatbox', normal: 'Yönetimi' } },
    { label: 'Mağaza', title: { bold: 'Sanal', normal: 'Mağaza' } },
    { label: 'Mesajlaşma', title: { bold: 'Mesajlaşma', normal: 'Kayıtları' } },
    { label: 'İstatistik', title: { bold: 'İstatistik', normal: '& Rapor' } },
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
            
            {/* Chatbox Management Controls - başlık Chatbox olduğunda göster */}
            {pageTitle.bold === 'Chatbox' && (
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
                    {chatboxList.map((chatbox) => (
                      <div
                        key={chatbox.id}
                        onClick={() => {
                          setSelectedChatbox(chatbox)
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
                    ))}
                  </div>
                )}
              </div>

              {/* New Chatbox Button */}
              <button 
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
                {/* Kayma animasyonu için çizgi - responsive genişlik ve pozisyon */}
                <div 
                  className="absolute bottom-0 h-0.5 transition-all duration-300 ease-in-out"
                  style={{
                    left: `${getUnderlinePosition(activeTabIndex)}px`,
                    width: `${getUnderlineWidth()}px`,
                    backgroundColor: themeColors.primary
                  }}
                ></div>
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
              {currentPage === 1 && <ChatboxManagement activeTab={activeTab} themeColors={themeColors} />}
              {currentPage === 2 && <VirtualStore themeColors={themeColors} storeList={storeList} setStoreList={setStoreList} />}
              {currentPage !== 1 && currentPage !== 2 && (
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
