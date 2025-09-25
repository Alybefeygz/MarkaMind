'use client'

import { Copy, ChevronDown, MessageSquare } from 'lucide-react'
import React, { useState } from 'react'

interface MessagingRecordsProps {
  themeColors?: {
    primary?: string
  }
  chatboxList?: Array<{
    id: number
    name: string
    status: string
    messages: number
    colors?: {
      primary?: string
    }
  }>
  selectedChatbox?: {
    id: number
    name: string
    colors?: {
      primary?: string
    }
  }
  onChatboxSelect?: (chatbox: any) => void
}

export default function MessagingRecords({
  themeColors = { primary: '#6F55FF' },
  chatboxList = [],
  selectedChatbox,
  onChatboxSelect
}: MessagingRecordsProps) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [currentSelectedChatbox, setCurrentSelectedChatbox] = useState(selectedChatbox || chatboxList[0])
  const [selectedConversation, setSelectedConversation] = useState<number | null>(null)

  // Update currentSelectedChatbox when selectedChatbox prop changes
  React.useEffect(() => {
    if (selectedChatbox) {
      setCurrentSelectedChatbox(selectedChatbox)
    }
  }, [selectedChatbox])

  // Reset selected conversation when chatbox changes
  React.useEffect(() => {
    setSelectedConversation(null)
  }, [currentSelectedChatbox?.id])

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedIndex(index)
      setTimeout(() => setCopiedIndex(null), 2000)
    })
  }

  const conversationsByChat = {
    1: [
      {
        id: 1,
        firstMessage: "Merhaba, ürün fiyatları hakkında bilgi alabilir miyim?",
        lastMessage: "Teşekkürler, yardımınız için çok memnun kaldım.",
        timestamp: "2 saat önce",
        messages: [
          { text: "Merhaba, ürün fiyatları hakkında bilgi alabilir miyim?", sender: "user", time: "14:30" },
          { text: "Merhaba! Tabii ki, hangi ürün hakkında bilgi almak istiyorsunuz?", sender: "bot", time: "14:31" },
          { text: "Laptop modellerini merak ediyorum", sender: "user", time: "14:32" },
          { text: "Laptop modellerimiz 15.000₺ ile 45.000₺ arasında değişmektedir. Detaylar için ürün sayfamızı ziyaret edebilirsiniz.", sender: "bot", time: "14:33" },
          { text: "Teşekkürler, yardımınız için çok memnun kaldım.", sender: "user", time: "14:35" }
        ]
      },
      {
        id: 2,
        firstMessage: "Kargo süresi ne kadar?",
        lastMessage: "Tamam, sipariş veriyorum o zaman.",
        timestamp: "5 saat önce",
        messages: [
          { text: "Kargo süresi ne kadar?", sender: "user", time: "11:20" },
          { text: "Kargo süremiz İstanbul içi 1-2 gün, Türkiye geneli 2-5 gündür.", sender: "bot", time: "11:21" },
          { text: "Tamam, sipariş veriyorum o zaman.", sender: "user", time: "11:22" }
        ]
      },
      {
        id: 3,
        firstMessage: "Bu üründe indirim var mı?",
        lastMessage: "Anlıyorum, başka ürünlere bakacağım.",
        timestamp: "1 gün önce",
        messages: [
          { text: "Bu üründe indirim var mı?", sender: "user", time: "16:45" },
          { text: "Şu anda bu üründe indirim bulunmuyor, ancak kampanyalarımızı takip edebilirsiniz.", sender: "bot", time: "16:46" },
          { text: "Anlıyorum, başka ürünlere bakacağım.", sender: "user", time: "16:47" }
        ]
      }
    ],
    2: [
      {
        id: 4,
        firstMessage: "Teknik destek alabilir miyim?",
        lastMessage: "Sorunu çözdünüz, teşekkür ederim!",
        timestamp: "1 saat önce",
        messages: [
          { text: "Teknik destek alabilir miyim?", sender: "user", time: "15:20" },
          { text: "Tabii ki! Hangi konuda yardıma ihtiyacınız var?", sender: "bot", time: "15:21" },
          { text: "Ürünüm çalışmıyor, nasıl çözebilirim?", sender: "user", time: "15:22" },
          { text: "Öncelikle cihazı yeniden başlatmayı deneyiniz. Sonrasında güncelleme kontrolü yapın.", sender: "bot", time: "15:23" },
          { text: "Sorunu çözdünüz, teşekkür ederim!", sender: "user", time: "15:35" }
        ]
      },
      {
        id: 5,
        firstMessage: "Garanti kapsamı nedir?",
        lastMessage: "Anlaşıldı, garanti süreci başlatılsın.",
        timestamp: "3 saat önce",
        messages: [
          { text: "Garanti kapsamı nedir?", sender: "user", time: "13:10" },
          { text: "Ürünlerimizde 2 yıl garanti bulunmaktadır. Üretim hatalarını kapsar.", sender: "bot", time: "13:11" },
          { text: "Ürünüm bozuldu, garanti kapsamında mı?", sender: "user", time: "13:12" },
          { text: "Ürününüzü inceleyebilirim. Fatura ve ürün fotoğrafını gönderebilir misiniz?", sender: "bot", time: "13:13" },
          { text: "Anlaşıldı, garanti süreci başlatılsın.", sender: "user", time: "13:15" }
        ]
      },
      {
        id: 6,
        firstMessage: "Yazılım güncellemesi nasıl yapılır?",
        lastMessage: "Güncelleme tamamlandı, çok teşekkürler!",
        timestamp: "6 saat önce",
        messages: [
          { text: "Yazılım güncellemesi nasıl yapılır?", sender: "user", time: "10:30" },
          { text: "Ayarlar menüsünden 'Güncelleme' seçeneğine tıklayın.", sender: "bot", time: "10:31" },
          { text: "Bulamadım, adım adım anlatabilir misiniz?", sender: "user", time: "10:32" },
          { text: "1. Ana menü -> Ayarlar 2. Sistem -> Güncelleme 3. 'Güncellemeleri kontrol et' butonuna basın", sender: "bot", time: "10:33" },
          { text: "Güncelleme tamamlandı, çok teşekkürler!", sender: "user", time: "10:45" }
        ]
      }
    ],
    3: [
      {
        id: 7,
        firstMessage: "Premium üyelik avantajları nelerdir?",
        lastMessage: "Premium üyelik için başvuruyorum.",
        timestamp: "30 dakika önce",
        messages: [
          { text: "Premium üyelik avantajları nelerdir?", sender: "user", time: "15:45" },
          { text: "Premium üyelikle öncelikli destek, özel indirimler ve ücretsiz kargo avantajınız olur.", sender: "bot", time: "15:46" },
          { text: "Aylık ücreti ne kadar?", sender: "user", time: "15:47" },
          { text: "Aylık 49₺, yıllık 490₺'dir. Yıllık üyelikle 2 ay ücretsiz kazanırsınız.", sender: "bot", time: "15:48" },
          { text: "Premium üyelik için başvuruyorum.", sender: "user", time: "15:50" }
        ]
      },
      {
        id: 8,
        firstMessage: "VIP destek hattına nasıl ulaşabilirim?",
        lastMessage: "Numarayı kaydettim, teşekkürler.",
        timestamp: "2 saat önce",
        messages: [
          { text: "VIP destek hattına nasıl ulaşabilirim?", sender: "user", time: "14:00" },
          { text: "Premium üyelerimiz için özel VIP hattımız: 0850-123-4567", sender: "bot", time: "14:01" },
          { text: "Numarayı kaydettim, teşekkürler.", sender: "user", time: "14:02" }
        ]
      },
      {
        id: 9,
        firstMessage: "Özel kampanyalardan nasıl haberdar olurum?",
        lastMessage: "E-posta listesine kaydoldum.",
        timestamp: "4 saat önce",
        messages: [
          { text: "Özel kampanyalardan nasıl haberdar olurum?", sender: "user", time: "12:15" },
          { text: "Premium üyelerimize özel kampanyaları e-posta ile bildiriyoruz.", sender: "bot", time: "12:16" },
          { text: "E-posta adresimi güncelleyebilir miyim?", sender: "user", time: "12:17" },
          { text: "Tabii ki! Profil ayarlarından e-posta adresinizi güncelleyebilirsiniz.", sender: "bot", time: "12:18" },
          { text: "E-posta listesine kaydoldum.", sender: "user", time: "12:20" }
        ]
      }
    ]
  }

  const conversations = conversationsByChat[currentSelectedChatbox?.id] || conversationsByChat[1] || []

  const integrationElements = [
    {
      id: 1,
      title: "Chatbox Mesajları",
      subtitle: "Web Sitesi Entegrasyonu",
      code: `<script>
window.MarkaMindWidgetConfig = {
  chatbotId: "19547356-af13-41a8-8"
};
</script>
<script src="https://dashboard.markamind.ai/api/chatbot-widget"></script>`
    },
    {
      id: 2,
      title: "Konuşma Detayları",
      subtitle: "Seçili Konuşma",
      code: `<script>
window.MarkaMindMobileConfig = {
  apiKey: "mm_mobile_19547356",
  theme: "auto"
};
</script>
<script src="https://dashboard.markamind.ai/api/mobile-widget"></script>`
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50/50 p-3 sm:p-4 lg:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Integration Elements - Side by Side */}
        <div className="grid grid-cols-1 lg:grid-cols-10 gap-6 lg:gap-8">
          {integrationElements.map((element, index) => (
            <div key={element.id}
                 className={`bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out translate-y-0 scale-100 w-full h-[70vh] ${
                   element.id === 1 ? 'lg:col-span-3' : 'lg:col-span-7'
                 }`}
                 style={{
                   borderColor: 'rgb(229, 231, 235)',
                   animationDelay: `${150 + index * 150}ms`
                 }}>

              {/* Header */}
              <div className="flex items-center p-4 sm:p-6 lg:p-8 border-b border-gray-200">
                <h3 className="text-xl sm:text-2xl lg:text-3xl">
                  <span className="font-bold bg-gradient-to-r bg-clip-text text-transparent"
                        style={{backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.primary})`}}>
                    {element.id === 2 && selectedConversation ?
                      conversations.find(c => c.id === selectedConversation)?.firstMessage.split(' ')[0] || element.title.split(' ')[0]
                      : element.title.split(' ')[0]
                    }
                  </span>
                  <span className="font-normal bg-gradient-to-r bg-clip-text text-transparent"
                        style={{backgroundImage: `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.primary})`}}>
                    {element.id === 2 && selectedConversation ?
                      conversations.find(c => c.id === selectedConversation)?.firstMessage.split(' ').slice(1).join(' ') || element.title.split(' ')[1]
                      : element.title.split(' ')[1]
                    }
                  </span>
                </h3>
              </div>

              {/* Content - Conversations or Code */}
              <div className="flex-1 flex flex-col overflow-y-auto">
                {element.id === 1 ? (
                  /* Conversations List */
                  <div className="divide-y divide-gray-200">
                    {conversations.map((conversation, index) => (
                      <div
                        key={conversation.id}
                        className={`h-24 p-6 transition-colors cursor-pointer flex items-center ${
                          selectedConversation === conversation.id
                            ? 'bg-blue-50/50 border-l-4 border-blue-500'
                            : 'hover:bg-gray-50/50'
                        }`}
                        onClick={() => setSelectedConversation(conversation.id)}
                      >
                        <div className="w-full">
                          <h4 className="text-lg font-medium text-gray-900 mb-1 truncate">
                            {conversation.firstMessage}
                          </h4>
                          <p className="text-base text-gray-600 mb-2 truncate">
                            {conversation.lastMessage}
                          </p>
                          <span className="text-sm text-gray-500 font-medium">
                            {conversation.timestamp}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  /* Chat Messages Display */
                  <div className="p-4 sm:p-6 lg:p-8">
                    {selectedConversation ? (
                      <div className="space-y-4">
                        {conversations.find(c => c.id === selectedConversation)?.messages.map((message, msgIndex) => (
                          <div key={msgIndex} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div
                              className={`max-w-[70%] p-4 rounded-2xl ${
                                message.sender === 'user'
                                  ? 'rounded-br-md'
                                  : 'rounded-bl-md'
                              }`}
                              style={{
                                backgroundColor: message.sender === 'user'
                                  ? currentSelectedChatbox?.colors?.userMessage || '#3B82F6'
                                  : currentSelectedChatbox?.colors?.aiMessage || '#F3F4F6',
                                color: message.sender === 'user'
                                  ? currentSelectedChatbox?.colors?.userTextColor || '#FFFFFF'
                                  : currentSelectedChatbox?.colors?.aiTextColor || '#374151'
                              }}
                            >
                              <p className="text-sm leading-relaxed">{message.text}</p>
                              <span className={`text-xs mt-2 block opacity-75`}>
                                {message.time}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="flex items-center justify-center h-full text-gray-500">
                        <div className="text-center">
                          <MessageSquare className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                          <p className="text-lg">Bir konuşma seçin</p>
                          <p className="text-sm">Mesajları görüntülemek için soldaki listeden bir konuşma seçin</p>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

            </div>
          ))}
        </div>
      </div>
    </div>
  )
}