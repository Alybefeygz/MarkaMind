"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import ThirdRobotChatBox from "./ThirdRobotChatBox"
import { useRobotChat } from "../../../hooks/use-api"
import { useIsMobile } from "../../../hooks/use-mobile"
import { toast } from "sonner"

interface ThirdRobotProps {
  onChatToggle: (robotId: string, isOpen: boolean) => void
  isOtherChatOpen: boolean
  isFloating?: boolean
}

interface ChatResponse {
  answer: string;
  citations?: any[];
  context_used?: boolean;
  response_time?: number;
  session_id?: string;
}

interface Citation {
  source: string
  content: string
  similarity: number
  chunk_index: number
  pdf_type: string
}

interface Message {
  id: number
  text: string
  isUser: boolean
  timestamp: Date
  status?: 'loading' | 'ok' | 'error'
  citations?: Citation[]
  context_used?: boolean
}

export default function ThirdRobot({ onChatToggle, isOtherChatOpen, isFloating = false }: ThirdRobotProps) {
  // Mobile detection
  const isMobile = useIsMobile()
  
  // Chat state
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Merhaba, ben **çocuk SidrexGPT**. Bağışıklığımı güçlendiren desteğimle hasta olma ihtimalimi azaltıyor, kendimi hep koruma altında hissediyorum!",
      isUser: false,
      timestamp: new Date(),
      status: 'ok'
    },
    {
      id: 2,
      text: "Size nasıl yardımcı olabilirim?",
      isUser: false,
      timestamp: new Date(),
      status: 'ok'
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [chatPosition, setChatPosition] = useState({ top: 0, left: 0 })

  // Robot Chat API integration
  const { sendMessage: sendChatMessage, loading: chatLoading } = useRobotChat('sidrexgpt-kids')

  // Animation state
  const buttonRef = useRef<HTMLButtonElement>(null)
  const [isHovered, setIsHovered] = useState(false)

  // Close chat when other chat opens
  useEffect(() => {
    if (isOtherChatOpen && isChatOpen) {
      setIsChatOpen(false)
      setIsHovered(false)
    }
  }, [isOtherChatOpen, isChatOpen])

  // Calculate responsive dimensions for chatbox
  const calculateChatboxDimensions = () => {
    const screenWidth = window.innerWidth
    let chatboxWidth = 384
    let chatboxHeight = 480
    
    if (screenWidth < 500) {
      const scale = screenWidth / 500
      chatboxWidth = Math.max(280, 384 * scale)
      chatboxHeight = Math.max(360, 480 * scale)
    }
    
    return { chatboxWidth, chatboxHeight }
  }

  // Update chatbox position when mobile state changes while chat is open
  useEffect(() => {
    if (isChatOpen && !isFloating && buttonRef.current) {
      if (isMobile) {
        // Mobile: center chatbox on screen with 1px right offset
        const rect = buttonRef.current.getBoundingClientRect()
        const screenHeight = window.innerHeight
        const screenWidth = window.innerWidth
        
        // Calculate responsive dimensions using centralized function
        const { chatboxWidth, chatboxHeight } = calculateChatboxDimensions()
        
        const verticalCenter = screenHeight / 2
        const horizontalCenter = screenWidth / 2
        const chatboxTop = verticalCenter - (chatboxHeight / 2) - 140 // 140px higher (60px down from previous)
        const chatboxLeft = horizontalCenter - (chatboxWidth / 2) + 1 // Center + 1px right offset
        
        setChatPosition({
          top: chatboxTop - rect.top - window.scrollY,
          left: chatboxLeft - rect.left - window.scrollX,
        })
      } else {
        // Desktop: original position
        setChatPosition({
          top: -390,
          left: -420,
        })
      }
    }
  }, [isMobile, isChatOpen, isFloating])

  const sendMessage = async () => {
    if (inputValue.trim() === "" || chatLoading) return

    const userMessage: Message = {
      id: Date.now(),
      text: inputValue,
      isUser: true,
      timestamp: new Date(),
      status: 'ok'
    }

    const loadingMessage: Message = {
        id: Date.now() + 1,
        text: "...",
        isUser: false,
        timestamp: new Date(),
        status: 'loading',
    }

    setMessages((prev) => [...prev, userMessage, loadingMessage])
    const messageText = inputValue
    setInputValue("")

    try {
      const response = await sendChatMessage(messageText) as ChatResponse
      
      if (response && (response as any).robot_response) {
        const botResponse: Message = {
          id: loadingMessage.id, // Use the same ID to update
          text: (response as any).robot_response,
          isUser: false,
          timestamp: new Date(),
          status: 'ok',
          citations: (response as any).citations || [],
          context_used: (response as any).context_used || false,
        }
        setMessages((prev) => prev.map(msg => msg.id === loadingMessage.id ? botResponse : msg))
      } else {
        const errorResponse: Message = {
            id: loadingMessage.id,
            text: "Yanıt alınamadı, lütfen tekrar deneyin.",
            isUser: false,
            timestamp: new Date(),
            status: 'error',
        }
        setMessages((prev) => prev.map(msg => msg.id === loadingMessage.id ? errorResponse : msg));
      }
    } catch (error: any) {
      console.error('Chat error:', error)
      toast.error(error.message || 'Mesaj gönderilemedi')
      
      const errorResponse: Message = {
        id: loadingMessage.id,
        text: "Üzgünüm, şu anda bir sorun yaşıyorum. Lütfen daha sonra tekrar deneyin.",
        isUser: false,
        timestamp: new Date(),
        status: 'error'
      }
      setMessages((prev) => prev.map(msg => msg.id === loadingMessage.id ? errorResponse : msg));
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      sendMessage()
    }
  }

  const toggleChat = () => {
    if (!isChatOpen && buttonRef.current && !isFloating) {
      // For iframe context, position chatbox relative to robot
      if (isMobile) {
        // Mobile: center chatbox on screen with 1px right offset
        const rect = buttonRef.current.getBoundingClientRect()
        const screenHeight = window.innerHeight
        const screenWidth = window.innerWidth
        
        // Calculate responsive dimensions using centralized function
        const { chatboxWidth, chatboxHeight } = calculateChatboxDimensions()
        
        const verticalCenter = screenHeight / 2
        const horizontalCenter = screenWidth / 2
        const chatboxTop = verticalCenter - (chatboxHeight / 2) - 140 // 140px higher (60px down from previous)
        const chatboxLeft = horizontalCenter - (chatboxWidth / 2) + 1 // Center + 1px right offset
        
        setChatPosition({
          top: chatboxTop - rect.top - window.scrollY,
          left: chatboxLeft - rect.left - window.scrollX,
        })
      } else {
        // Desktop: original position
        setChatPosition({
          top: -390,
          left: -420,
        })
      }
    }
    const newChatState = !isChatOpen
    setIsChatOpen(newChatState)
    onChatToggle("third", newChatState)
  }

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        onClick={toggleChat}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => {
          if (!isChatOpen) {
            setIsHovered(false)
          }
        }}
        className={`w-24 h-24 rounded-full shadow-2xl hover:shadow-xl transition-all duration-300 transform hover:scale-105 cursor-pointer flex items-center justify-center relative overflow-visible ${
          isChatOpen || isHovered ? "third-robot-active" : ""
        }`}
        style={{
          backgroundColor: "#FEFBEF",
          border: "2px solid #FFC429",
        }}
      >
        {/* Z harfleri for third robot only - positioned in top-right corner */}
        <div className="absolute -top-2 -right-2 pointer-events-none third-robot-z">
          {/* Ana Z - en küçük */}
          <div
            className="absolute w-4 h-4 flex items-center justify-center text-yellow-400 font-bold text-sm"
            style={{ top: "0px", right: "0px" }}
          >
            Z
          </div>
          {/* Üst Z - normal boyut */}
          <div
            className="absolute w-6 h-6 flex items-center justify-center text-yellow-400 font-bold text-lg"
            style={{ top: "-20px", right: "-12px" }}
          >
            Z
          </div>
          {/* Orta Z - biraz küçük */}
          <div
            className="absolute w-5 h-5 flex items-center justify-center text-yellow-400 font-bold text-base"
            style={{ top: "-16px", right: "12px" }}
          >
            Z
          </div>
        </div>
        {/* Robot Mascot */}
        <div className={`robot-mascot-container ${isChatOpen ? "chat-active" : ""}`}>
          <div className="robot-head-third">
            {/* Robot Antenna - Yellow antenna for third robot */}
            <div className="robot-antenna-yellow"></div>

            {/* Robot Ears */}
            <div className="robot-ear-third robot-ear-left"></div>
            <div className="robot-ear-third robot-ear-right"></div>
            <div className="robot-face-third">
              {/* Third robot eyes */}
              <div className="robot-third-eyes"></div>
              {/* Third robot hover eyes - circular eyes that appear on hover */}
              <div className="robot-third-hover-eyes left"></div>
              <div className="robot-third-hover-eyes right"></div>
              {/* Third robot mouth */}
              <div className="robot-third-mouth"></div>
            </div>
          </div>
        </div>
        {/* Robot Shield - appears on hover */}
        <div className="robot-shield"></div>
      </button>

      {/* Chat Box */}
      {isChatOpen && (
        <ThirdRobotChatBox
          messages={messages}
          inputValue={inputValue}
          setInputValue={setInputValue}
          sendMessage={sendMessage}
          handleKeyPress={handleKeyPress}
          onClose={() => {
            setIsChatOpen(false)
            setIsHovered(false)
          }}
          position={chatPosition}
          isFloating={isFloating}
          isLoading={chatLoading}
        />
      )}
    </div>
  )
}
