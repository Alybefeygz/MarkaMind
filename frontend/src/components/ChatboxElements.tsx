'use client'

import { MessageSquare, Send } from 'lucide-react'
import { useState } from 'react'

interface ChatboxElementsProps {
  chatboxTitle?: string
  initialMessage?: string
  colors?: {
    primary?: string
    aiMessage?: string
    userMessage?: string
    borderColor?: string
    aiTextColor?: string
    userTextColor?: string
    buttonPrimary?: string
    buttonIcon?: string
  }
  isVisible?: boolean
  onToggle?: () => void
  className?: string
  style?: React.CSSProperties
  animationClass?: string
}

interface Message {
  id: number
  text: string
  sender: 'user' | 'bot'
  timestamp: Date
}

export default function ChatboxElements({
  chatboxTitle = 'Zzen Chatbox',
  initialMessage = "Hello! It's Orbina here!",
  colors = {
    primary: '#7B4DFA',
    aiMessage: '#E5E7EB',
    userMessage: '#7B4DFA',
    borderColor: '#B794F6',
    aiTextColor: '#1F2937',
    userTextColor: '#FFFFFF',
    buttonPrimary: '#7B4DFA',
    buttonIcon: '#FFFFFF'
  },
  isVisible = true,
  onToggle,
  className = '',
  style = {},
  animationClass = ''
}: ChatboxElementsProps) {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, text: initialMessage, sender: 'bot', timestamp: new Date() }
  ])

  const handleSendMessage = () => {
    if (message.trim()) {
      const userMessage: Message = {
        id: messages.length + 1,
        text: message.trim(),
        sender: 'user',
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, userMessage])
      setMessage('')
      
      setTimeout(() => {
        const botMessage: Message = {
          id: messages.length + 2,
          text: "Mesajınız için teşekkürler! Bu bir demo chatbox'tır. Gerçek bir backend bağlantısı henüz mevcut değildir.",
          sender: 'bot',
          timestamp: new Date()
        }
        setMessages(prev => [...prev, botMessage])
      }, 2000)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSendMessage()
    }
  }

  return (
    <div className={`flex flex-col xl:flex-row xl:items-end gap-4 lg:gap-6 xl:gap-12 ${className} ${animationClass}`} style={style}>
      {/* Chatbox Dikdörtgen Alanı */}
      <div 
        className="bg-white border-2 rounded-2xl flex flex-col w-full max-w-full lg:w-[500px] xl:w-[550px] 2xl:w-[600px] order-1 lg:h-[750px] xl:h-[800px] 2xl:h-[850px] overflow-hidden"
        style={{ 
          minHeight: '400px',
          borderColor: colors.primary,
          transform: isVisible ? 'translateX(0)' : 'translateX(32px)',
          opacity: isVisible ? 1 : 0,
          transition: 'opacity 0.3s ease-out, transform 0.3s ease-out'
        }}
      >
        {/* Chatbox Header */}
        <div className="flex items-center p-4 sm:p-6 lg:p-8 border-b border-gray-200">
          <h3 className="text-lg sm:text-xl lg:text-2xl xl:text-3xl font-bold text-gray-900">{chatboxTitle}</h3>
        </div>

        {/* Messages Area */}
        <div className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto">
          {messages.map((msg) => (
            <div key={msg.id} className={`mb-3 sm:mb-4 lg:mb-6 ${msg.sender === 'user' ? 'flex justify-end' : ''}`}>
              <div className={`p-3 sm:p-4 lg:p-6 rounded-xl lg:rounded-2xl max-w-[85%] sm:max-w-xs lg:max-w-md ${
                msg.sender === 'user' 
                  ? 'text-white ml-auto' 
                  : 'text-gray-800'
              }`}
              style={msg.sender === 'user' 
                ? { backgroundColor: colors.userMessage, color: colors.userTextColor } 
                : { backgroundColor: colors.aiMessage, color: colors.aiTextColor }
              }
              >
                <p className="text-sm sm:text-base lg:text-lg leading-relaxed">{msg.text}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Message Input */}
        <div className="p-4 sm:p-6 lg:p-8 border-t border-gray-200">
          <div className="flex items-center bg-gray-50 rounded-lg lg:rounded-xl p-3 sm:p-4 lg:p-5 w-full overflow-hidden">
            <input
              type="text"
              placeholder="Mesaj gönder..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1 bg-transparent text-sm sm:text-base lg:text-lg text-gray-700 placeholder-gray-400 focus:outline-none min-w-0"
            />
            <button 
              onClick={handleSendMessage}
              className="ml-2 sm:ml-3 p-1.5 sm:p-2 hover:scale-110 transition-all duration-300 flex-shrink-0"
            >
              <Send className="w-5 sm:w-6 lg:w-7 h-5 sm:h-6 lg:h-7" style={{ color: colors.primary }} />
            </button>
          </div>
          
          <div className="text-center mt-3 sm:mt-4 lg:mt-5">
            <span className="text-xs sm:text-sm lg:text-base text-gray-400">MarkaMind</span>
            <span className="text-xs sm:text-sm lg:text-base text-gray-400 ml-1">tarafından geliştirildi</span>
          </div>
        </div>
      </div>

      {/* Toggle Button */}
      <div className="order-2 flex justify-end xl:block">
        <button
          onClick={onToggle}
          className="rounded-full flex items-center justify-center cursor-pointer group shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110"
          style={{ 
            width: '100px', 
            height: '100px',
            backgroundColor: colors.buttonPrimary,
            border: `3px solid ${colors.borderColor}`
          }}
        >
          <MessageSquare 
            className="w-12 h-12" 
            strokeWidth={1.2} 
            style={{ color: colors.buttonIcon }}
          />
        </button>
      </div>
    </div>
  )
}