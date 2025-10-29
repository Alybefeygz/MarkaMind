'use client'

import { MessageSquare, Send } from 'lucide-react'
import { useState } from 'react'

interface VirtualStoreChatboxAndButtonsProps {
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

export default function VirtualStoreChatboxAndButtons({
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
}: VirtualStoreChatboxAndButtonsProps) {
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
    <div className={`flex flex-col xl:flex-row xl:items-end ${isVisible ? 'gap-4 lg:gap-6 xl:gap-12' : 'gap-0'} ${className} ${animationClass}`} style={style}>
      {/* Chatbox Dikdörtgen Alanı */}
      {isVisible && (
        <div
          className="bg-white border-2 rounded-2xl flex flex-col w-full max-w-full lg:w-[350px] xl:w-[380px] 2xl:w-[400px] order-1 lg:h-[500px] xl:h-[520px] 2xl:h-[550px] overflow-hidden"
          style={{
            minHeight: '350px',
            borderColor: colors.primary
          }}
        >
        {/* Chatbox Header */}
        <div className="flex items-center p-3 sm:p-4 lg:p-5 border-b border-gray-200">
          <h3 className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">{chatboxTitle}</h3>
        </div>

        {/* Messages Area */}
        <div className="flex-1 p-3 sm:p-4 lg:p-5 overflow-y-auto">
          {messages.map((msg) => (
            <div key={msg.id} className={`mb-2 sm:mb-3 ${msg.sender === 'user' ? 'flex justify-end' : ''}`}>
              <div className={`p-2 sm:p-3 rounded-lg lg:rounded-xl max-w-[85%] sm:max-w-xs ${
                msg.sender === 'user'
                  ? 'text-white ml-auto'
                  : 'text-gray-800'
              }`}
              style={msg.sender === 'user'
                ? { backgroundColor: colors.userMessage, color: colors.userTextColor }
                : { backgroundColor: colors.aiMessage, color: colors.aiTextColor }
              }
              >
                <p className="text-xs sm:text-sm leading-relaxed">{msg.text}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Message Input */}
        <div className="p-3 sm:p-4 border-t border-gray-200">
          <div className="flex items-center bg-gray-50 rounded-lg p-2 sm:p-3 w-full overflow-hidden">
            <input
              type="text"
              placeholder="Mesaj gönder..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1 bg-transparent text-xs sm:text-sm text-gray-700 placeholder-gray-400 focus:outline-none min-w-0"
            />
            <button
              onClick={handleSendMessage}
              className="ml-2 p-1.5 hover:scale-110 transition-all duration-300 flex-shrink-0"
            >
              <Send className="w-4 sm:w-5 h-4 sm:h-5" style={{ color: colors.primary }} />
            </button>
          </div>

          <div className="text-center mt-2 sm:mt-3">
            <span className="text-[10px] sm:text-xs text-gray-400">MarkaMind</span>
            <span className="text-[10px] sm:text-xs text-gray-400 ml-1">tarafından geliştirildi</span>
          </div>
        </div>
        </div>
      )}

      {/* Toggle Button */}
      <div className="order-2 flex justify-end xl:block">
        <button
          onClick={onToggle}
          className="rounded-full flex items-center justify-center cursor-pointer group shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110"
          style={{
            width: '75px',
            height: '75px',
            backgroundColor: colors.buttonPrimary,
            border: `2.5px solid ${colors.borderColor}`
          }}
        >
          <MessageSquare
            className="w-9 h-9"
            strokeWidth={1.2}
            style={{ color: colors.buttonIcon }}
          />
        </button>
      </div>
    </div>
  )
}
