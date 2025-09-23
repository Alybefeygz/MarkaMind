'use client'

import { MessageSquare, Send, X, Minimize2, ArrowLeft, Star, User } from 'lucide-react'
import { useState } from 'react'

export default function ChatboxPreview() {
  const [isChatboxOpen, setIsChatboxOpen] = useState(true) // Başta açık olsun
  const [message, setMessage] = useState('')
  const [showRating, setShowRating] = useState(false)
  const [selectedStars, setSelectedStars] = useState(0)

  // Görseldeki mesajları taklit eden örnek mesajlar
  const messages = [
    { 
      id: 1, 
      type: 'user', 
      text: 'sen kimsin', 
      time: '17 dakika önce',
      author: 'Sen'
    },
    { 
      id: 2, 
      type: 'bot', 
      text: 'Ben, Orbina AI ekibi tarafından geliştirilmiş yardımcı bir asistanım. Size bilgi sağlamak ve sorularınızı yanıtlamak için buradayım. Size nasıl yardımcı olabilirim?', 
      time: '17 dakika önce',
      author: 'YazıgGPT\'s'
    },
    { 
      id: 3, 
      type: 'bot', 
      text: 'Bu konuşma sona erdi.', 
      time: '',
      author: 'YazıgGPT\'s'
    },
    { 
      id: 4, 
      type: 'rating', 
      text: 'Deneyiminizi değerlendirin! ⭐', 
      time: '',
      author: ''
    },
    { 
      id: 5, 
      type: 'system', 
      text: 'Bu konuşmaya mesaj gönderemezsiniz.', 
      time: '2 dakika önce',
      author: 'YazıgGPT\'s'
    }
  ]

  const handleSendMessage = () => {
    if (message.trim()) {
      // Mesaj gönderme mantığı burada olacak
      setMessage('')
    }
  }

  const handleStarClick = (starIndex) => {
    setSelectedStars(starIndex + 1)
  }

  return (
    <div className="h-screen bg-gradient-to-br from-purple-50 to-indigo-100 relative overflow-hidden p-8">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute top-20 left-20 w-40 h-40 border-2 border-purple-300 rounded-full"></div>
        <div className="absolute bottom-32 left-32 w-24 h-24 border border-indigo-200 rounded-full"></div>
        <div className="absolute top-40 right-40 w-16 h-16 bg-purple-200 rounded-full"></div>
      </div>
      
      {/* Preview Content */}
      <div className="flex items-center justify-center h-full">
        <div className="text-center mb-20">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Chatbox Önizleme</h2>
          <p className="text-gray-600 mb-8 max-w-md">Chatbox&apos;ınızın müşteriler tarafından nasıl görüneceğini test edin. Aşağıdaki chatbox ile etkileşime geçebilirsiniz.</p>
        </div>
      </div>

      {/* Floating Toggle Button */}
      <button
        onClick={() => setIsChatboxOpen(!isChatboxOpen)}
        className={`fixed bottom-8 right-8 w-14 h-14 rounded-full shadow-lg transition-all duration-300 flex items-center justify-center z-50 ${
          isChatboxOpen 
            ? 'bg-gray-500 hover:bg-gray-600' 
            : 'bg-gradient-to-r from-[#6434F8] to-[#7D56F9] hover:shadow-xl hover:scale-105'
        }`}
      >
        {isChatboxOpen ? (
          <X className="w-5 h-5 text-white" />
        ) : (
          <MessageSquare className="w-5 h-5 text-white" />
        )}
      </button>

      {/* Orbina Chatbox Widget */}
      <div className={`fixed bottom-24 right-8 w-96 bg-white rounded-2xl shadow-2xl transition-all duration-300 ease-in-out z-40 border border-purple-200 ${
        isChatboxOpen 
          ? 'opacity-100 visible translate-y-0 scale-100' 
          : 'opacity-0 invisible translate-y-8 scale-95'
      }`}>
        
        {/* Chatbox Header */}
        <div className="bg-gradient-to-r from-purple-500 to-indigo-600 p-4 rounded-t-2xl flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <ArrowLeft className="w-5 h-5 text-white cursor-pointer hover:bg-white/10 rounded p-0.5" />
            <div>
              <h3 className="text-white font-semibold text-lg">Orbina</h3>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="p-4 h-96 overflow-y-auto space-y-4 bg-gray-50">
          {messages.map((msg) => (
            <div key={msg.id}>
              {msg.type === 'user' && (
                <div className="flex justify-end">
                  <div className="max-w-[80%]">
                    <div className="flex items-center justify-end space-x-2 mb-1">
                      <span className="text-xs text-gray-500">{msg.author}</span>
                      <span className="text-xs text-gray-400">• {msg.time}</span>
                      <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                        <span className="text-xs text-white">✓✓</span>
                      </div>
                    </div>
                    <div className="bg-purple-600 text-white p-3 rounded-2xl rounded-tr-md">
                      <p className="text-sm">{msg.text}</p>
                    </div>
                  </div>
                </div>
              )}
              
              {msg.type === 'bot' && (
                <div className="flex justify-start">
                  <div className="max-w-[85%]">
                    <div className="flex items-center space-x-2 mb-1">
                      <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center">
                        <User className="w-3 h-3 text-purple-600" />
                      </div>
                      <span className="text-xs text-gray-600 font-medium">{msg.author}</span>
                      <span className="text-xs text-gray-400">• {msg.time}</span>
                    </div>
                    <div className="bg-white p-4 rounded-2xl rounded-tl-md shadow-sm border">
                      <p className="text-sm text-gray-800 leading-relaxed">{msg.text}</p>
                    </div>
                  </div>
                </div>
              )}

              {msg.type === 'rating' && (
                <div className="flex justify-center">
                  <div className="bg-gray-100 p-4 rounded-2xl text-center max-w-xs">
                    <p className="text-sm text-gray-700 mb-3 font-medium">{msg.text}</p>
                    <div className="flex justify-center space-x-1 mb-3">
                      {[...Array(5)].map((_, index) => (
                        <button
                          key={index}
                          onClick={() => handleStarClick(index)}
                          className="transition-colors duration-150"
                        >
                          <Star 
                            className={`w-6 h-6 ${
                              index < selectedStars 
                                ? 'text-yellow-400 fill-yellow-400' 
                                : 'text-gray-300'
                            } hover:text-yellow-400`}
                          />
                        </button>
                      ))}
                    </div>
                    <span className="text-xs text-gray-500">{selectedStars}/5</span>
                    <button className="ml-4 bg-purple-600 text-white px-3 py-1 rounded-full text-xs hover:bg-purple-700 transition-colors">
                      Gönder
                    </button>
                  </div>
                </div>
              )}

              {msg.type === 'system' && (
                <div className="flex justify-center">
                  <div className="flex items-center space-x-2">
                    <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center">
                      <User className="w-3 h-3 text-purple-600" />
                    </div>
                    <span className="text-xs text-gray-600">{msg.author}</span>
                    <span className="text-xs text-gray-400">• {msg.time}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Message Input - Disabled */}
        <div className="p-4 border-t border-gray-200 bg-white rounded-b-2xl">
          <div className="text-center text-sm text-gray-500 mb-2">
            Bu konuşmaya mesaj gönderemezsiniz.
          </div>
          <div className="flex items-center space-x-2 opacity-50">
            <input
              type="text"
              value=""
              disabled
              placeholder="Bu konuşma sona erdi..."
              className="flex-1 p-3 border border-gray-300 rounded-xl focus:outline-none text-sm bg-gray-50"
            />
            <button
              disabled
              className="p-3 bg-gray-300 text-gray-500 rounded-xl"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="text-center mt-2">
            <span className="text-xs text-gray-400">Orbina</span>
            <span className="text-xs text-gray-300 ml-1">tarafından geliştirildi</span>
          </div>
        </div>
      </div>
    </div>
  )
}