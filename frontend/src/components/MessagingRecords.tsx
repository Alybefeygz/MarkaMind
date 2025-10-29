'use client'

import { useState } from 'react'
import { User, Bot } from 'lucide-react'

interface MessagingRecordsProps {
  themeColors: {
    primary: string
    secondary: string
    text: string
  }
}

// Örnek mesajlaşma verileri
const conversationsData = [
  {
    id: 1,
    userName: 'Ziyaretçi #A7F2',
    date: '15 Ekim 2024',
    time: '14:32',
    firstMessage: 'iPhone 15 Pro hakkında bilgi alabilir miyim?',
    messages: [
      { sender: 'user', text: 'iPhone 15 Pro hakkında bilgi alabilir miyim?', time: '14:32' },
      { sender: 'bot', text: 'Merhaba! Tabii ki. iPhone 15 Pro modelimiz A17 Pro çip ile güçlendirilmiş, 6.1 inç Super Retina XDR ekrana sahip.', time: '14:32' },
      { sender: 'user', text: 'Fiyatı nedir?', time: '14:33' },
      { sender: 'bot', text: 'iPhone 15 Pro 128GB model 42.999 TL\'den başlayan fiyatlarla sunulmaktadır.', time: '14:33' },
      { sender: 'user', text: 'Kargo ücretsiz mi?', time: '14:34' },
      { sender: 'bot', text: 'Evet, 500 TL ve üzeri tüm siparişlerde kargo ücretsizdir.', time: '14:34' },
    ]
  },
  {
    id: 2,
    userName: 'Ziyaretçi #B3D9',
    date: '15 Ekim 2024',
    time: '13:15',
    firstMessage: 'AirPods Pro 2 stokta var mı?',
    messages: [
      { sender: 'user', text: 'AirPods Pro 2 stokta var mı?', time: '13:15' },
      { sender: 'bot', text: 'Evet, AirPods Pro 2. nesil ürünümüz stoklarımızda mevcuttur.', time: '13:15' },
      { sender: 'user', text: 'Kaç gün içinde teslim alırım?', time: '13:16' },
      { sender: 'bot', text: 'İstanbul içi 1 iş günü, diğer iller için 2-3 iş günü içinde teslim edilir.', time: '13:16' },
    ]
  },
  {
    id: 3,
    userName: 'Ziyaretçi #C8K1',
    date: '14 Ekim 2024',
    time: '16:45',
    firstMessage: 'MacBook Air M2 özellikleri nelerdir?',
    messages: [
      { sender: 'user', text: 'MacBook Air M2 özellikleri nelerdir?', time: '16:45' },
      { sender: 'bot', text: 'MacBook Air M2, Apple\'ın M2 çipi, 13.6 inç Liquid Retina ekran, 8GB RAM ve 256GB SSD ile geliyor.', time: '16:45' },
      { sender: 'user', text: 'Garanti süresi ne kadar?', time: '16:46' },
      { sender: 'bot', text: '2 yıl Apple Türkiye garantisi bulunmaktadır.', time: '16:46' },
      { sender: 'user', text: 'Teşekkürler', time: '16:47' },
      { sender: 'bot', text: 'Rica ederim! Başka sorunuz olursa her zaman buradayım.', time: '16:47' },
    ]
  },
  {
    id: 4,
    userName: 'Ziyaretçi #D5M7',
    date: '14 Ekim 2024',
    time: '11:20',
    firstMessage: 'İade politikanız nasıl işliyor?',
    messages: [
      { sender: 'user', text: 'İade politikanız nasıl işliyor?', time: '11:20' },
      { sender: 'bot', text: 'Ürünlerinizi teslim tarihinden itibaren 14 gün içinde kullanılmamış ve orijinal ambalajında iade edebilirsiniz.', time: '11:20' },
      { sender: 'user', text: 'İade ücreti var mı?', time: '11:21' },
      { sender: 'bot', text: 'Hayır, cayma hakkı kapsamındaki iadeler ücretsizdir. Kargo tarafımızdan karşılanır.', time: '11:21' },
    ]
  },
]

export default function MessagingRecords({ themeColors }: MessagingRecordsProps) {
  const [selectedConversation, setSelectedConversation] = useState(conversationsData[0])

  return (
    <div className="flex flex-col lg:flex-row gap-4 lg:gap-8 w-full mt-4 lg:mt-8 px-2 sm:px-4">

      {/* Mesajlar Kartı */}
      <div className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out translate-y-0 scale-100 w-full lg:w-1/4 h-[600px] lg:h-[700px]" style={{ borderColor: '#E5E7EB', animationDelay: '150ms' }}>
        <div className="flex items-center p-4 sm:p-6 lg:p-8 border-b border-gray-200">
          <h3 className="text-xl sm:text-2xl lg:text-3xl">
            <span
              className="font-bold bg-gradient-to-r bg-clip-text text-transparent"
              style={{
                backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
              }}
            >
              Mesajlar
            </span>
          </h3>
        </div>
        <div className="flex-1 p-2 sm:p-3 lg:p-4 flex flex-col overflow-y-auto gap-2">
          {conversationsData.map((conversation) => (
            <div
              key={conversation.id}
              onClick={() => setSelectedConversation(conversation)}
              className={`p-3 sm:p-4 rounded-lg cursor-pointer transition-all duration-200 border ${
                selectedConversation.id === conversation.id
                  ? 'border-2 shadow-md'
                  : 'border border-gray-200 hover:border-gray-300 hover:shadow-sm'
              }`}
              style={{
                borderColor: selectedConversation.id === conversation.id ? themeColors.primary : undefined,
                backgroundColor: selectedConversation.id === conversation.id ? `${themeColors.primary}08` : 'white'
              }}
            >
              <div className="flex items-start space-x-2 sm:space-x-3">
                <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm sm:text-base font-semibold text-gray-900 truncate">{conversation.userName}</p>
                  <p className="text-xs text-gray-500">{conversation.date} • {conversation.time}</p>
                  <p className="text-xs sm:text-sm text-gray-600 mt-1 line-clamp-2">{conversation.firstMessage}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Mesaj İçerikleri Kartı */}
      <div className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out translate-y-0 scale-100 w-full lg:w-3/4 h-[600px] lg:h-[700px]" style={{ borderColor: '#E5E7EB', animationDelay: '300ms' }}>
        <div className="flex items-center p-4 sm:p-6 lg:p-8 border-b border-gray-200">
          <div className="flex items-center space-x-3 flex-1">
            <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-gray-200 flex items-center justify-center">
              <User className="w-5 h-5 sm:w-6 sm:h-6 text-gray-600" />
            </div>
            <div>
              <h3 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900">
                {selectedConversation.userName}
              </h3>
              <p className="text-xs sm:text-sm text-gray-500">
                {selectedConversation.date} • {selectedConversation.time}
              </p>
            </div>
          </div>
        </div>
        <div className="flex-1 p-4 sm:p-6 lg:p-8 flex flex-col overflow-y-auto space-y-4">
          {selectedConversation.messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.sender === 'user' ? 'justify-start' : 'justify-end'}`}
            >
              <div
                className={`max-w-[75%] sm:max-w-[70%] rounded-2xl px-4 py-3 ${
                  message.sender === 'user'
                    ? 'bg-gray-100 text-gray-900'
                    : 'text-white'
                }`}
                style={{
                  background: message.sender === 'bot'
                    ? `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
                    : undefined
                }}
              >
                <div className="flex items-start space-x-2">
                  {message.sender === 'bot' && (
                    <Bot className="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <p className="text-sm sm:text-base leading-relaxed">{message.text}</p>
                    <p className={`text-xs mt-1 ${
                      message.sender === 'user' ? 'text-gray-500' : 'text-white opacity-75'
                    }`}>
                      {message.time}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
