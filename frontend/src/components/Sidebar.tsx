'use client'

import { Home, MessageSquare, ShoppingBag, MessageCircle, User, X, ChevronDown, Plus } from 'lucide-react'
import { useState, useEffect } from 'react'

const menuItems = [
  { icon: Home, label: 'Ana Sayfa', title: { bold: 'Ana', normal: 'Sayfa' } },
  { icon: MessageSquare, label: 'Chatbox', title: { bold: 'Chatbox', normal: 'Yönetimi' } },
  { icon: ShoppingBag, label: 'Mağaza', title: { bold: 'Sanal', normal: 'Mağaza' } },
  { icon: MessageCircle, label: 'Mesajlaşma', title: { bold: 'Mesajlaşma', normal: 'Kayıtları' } },
  { icon: User, label: 'Profil', title: { bold: '', normal: 'Profil' } },
]

interface SidebarProps {
  onTitleChange: (title: { bold: string; normal: string }) => void
  onPageChange: (pageIndex: number) => void
  isOpen: boolean
  onToggle: () => void
  themeColors: {
    primary: string
    secondary: string
    text: string
  }
}

// Chatbox listesi
const chatboxList = [
  { id: 1, name: 'iPhone 15 Pro Chatbox', status: 'active', messages: 1247 },
  { id: 2, name: 'MacBook Air Chatbox', status: 'active', messages: 890 },
  { id: 3, name: 'AirPods Pro Chatbox', status: 'inactive', messages: 456 }
]

export default function Sidebar({ onTitleChange, onPageChange, isOpen, onToggle, themeColors }: SidebarProps) {
  const [activeIndex, setActiveIndex] = useState(0)
  const [windowWidth, setWindowWidth] = useState(0)

  // Client-side'da window boyutunu al
  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth)
    }

    // İlk yüklemede boyutu ayarla
    handleResize()
    
    // Resize listener ekle
    window.addEventListener('resize', handleResize)
    
    return () => window.removeEventListener('resize', handleResize)
  }, [])
  
  // Chatbox dropdown state
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [selectedChatbox, setSelectedChatbox] = useState(chatboxList[0])
  
  const handleIconClick = (index: number) => {
    setActiveIndex(index)
    onTitleChange(menuItems[index].title)
    onPageChange(index)
  }

  return (
    <>
      {/* Dikey gri çizgi */}
      <div 
        className={`fixed w-px bg-[#E0E0E0] h-full transition-all duration-300 ease-in-out z-10 ${
          isOpen ? 'left-16 sm:left-20 md:left-24' : '-left-2'
        }`}
      ></div>


      {/* Sidebar X butonu */}
      <div className={`fixed transition-all duration-300 ease-in-out z-30 ${
        isOpen ? 'left-3 sm:left-4 md:left-6' : '-left-20'
      } top-4 sm:top-5 md:top-6`}>
        <button
          onClick={onToggle}
          className="w-10 h-10 sm:w-11 sm:h-11 md:w-12 md:h-12 flex items-center justify-center cursor-pointer group"
        >
          <X className="w-5 h-5 sm:w-5.5 sm:h-5.5 md:w-6 md:h-6 text-gray-600 group-hover:text-gray-800 group-hover:scale-110 transition-all duration-300 ease-in-out" strokeWidth={0.75} />
        </button>
      </div>

      {/* Aktif indicator çizgisi */}
      <div
        className={`fixed w-1 h-6 sm:h-7 md:h-8 rounded-full transition-all duration-300 ease-in-out z-20 ${
          isOpen ? 'opacity-100' : 'opacity-0'
        }`}
        style={{
          background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`,
          left: isOpen ? windowWidth < 640 ? '60px' : windowWidth < 768 ? '78px' : '94.5px' : '-10px',
          top: `calc(50% + ${(activeIndex - 2) * (windowWidth < 640 ? 52 : windowWidth < 768 ? 58 : 64) + (windowWidth < 640 ? 20 : windowWidth < 768 ? 22 : 24)}px)`,
          transform: 'translateY(-50%)'
        }}
      ></div>
      
      {/* Menu ikonları */}
      <div className={`fixed flex flex-col space-y-3 sm:space-y-3.5 md:space-y-4 z-10 transition-all duration-300 ease-in-out ${
        isOpen ? 'left-3 sm:left-4 md:left-6' : '-left-20'
      }`}
           style={{ 
             top: windowWidth < 640 ? 'calc(50% + 20px)' : windowWidth < 768 ? 'calc(50% + 22px)' : 'calc(50% + 24px)', 
             transform: 'translateY(-50%)' 
           }}>
        {menuItems.map((item, index) => {
          const Icon = item.icon
          const isActive = index === activeIndex
          return (
            <div
              key={index}
              className="w-10 h-10 sm:w-11 sm:h-11 md:w-12 md:h-12 flex items-center justify-center cursor-pointer relative group"
              title={item.label}
              onClick={() => handleIconClick(index)}
            >
              <div
                className={`absolute inset-0 w-12 h-12 sm:w-13 sm:h-13 md:w-14 md:h-14 rounded-full transition-opacity duration-300 ease-in-out ${isActive ? 'opacity-100' : 'opacity-0'}`}
                style={{
                  left: '-4px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                }}
              ></div>
              <Icon
                className={`w-5 h-5 sm:w-5.5 sm:h-5.5 md:w-6 md:h-6 relative z-10 transition-all duration-300 ease-in-out ${isActive ? 'text-white scale-125' : 'text-gray-600 group-hover:text-gray-800 group-hover:scale-110'}`}
                strokeWidth={isActive ? 1.2 : 0.75}
                style={{
                  strokeWidth: isActive ? 1.2 : undefined
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.strokeWidth = '1'
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.strokeWidth = '0.75'
                  }
                }}
              />
            </div>
          )
        })}
      </div>
    </>
  )
}