'use client'

import { useState, useEffect } from 'react'
import { User, Bot, Loader2, AlertCircle, RefreshCw } from 'lucide-react'
import { ChatboxResponse, SessionWithMessages, getChatbotUserMessages } from '@/lib/api'
import {
  formatMessageDate,
  formatMessageTime,
  getFirstUserMessage,
  getSessionDisplayName
} from '@/utils/messageHelpers'

interface MessagingRecordsProps {
  themeColors: {
    primary: string
    secondary: string
    text: string
  }
  selectedChatbox?: ChatboxResponse | null
}

export default function MessagingRecords({ themeColors, selectedChatbox }: MessagingRecordsProps) {
  // State Management
  const [sessions, setSessions] = useState<SessionWithMessages[]>([])
  const [selectedSession, setSelectedSession] = useState<SessionWithMessages | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  // Fetch sessions when chatbox changes
  useEffect(() => {
    if (selectedChatbox?.id) {
      fetchSessions()

      // Auto-refresh every 10 seconds
      const interval = setInterval(() => {
        fetchSessions(true) // Silent refresh
      }, 10000)

      return () => clearInterval(interval)
    } else {
      // Reset state when no chatbox selected
      setSessions([])
      setSelectedSession(null)
      setError(null)
    }
  }, [selectedChatbox?.id, currentPage])

  // Fetch sessions from API
  const fetchSessions = async (silent = false) => {
    if (!selectedChatbox?.id) return

    if (!silent) {
      setIsLoading(true)
      setError(null)
    }

    try {
      const response = await getChatbotUserMessages(selectedChatbox.id, {
        page: currentPage,
        size: 20,
        groupBySession: true,
        includeVisitorInfo: true
      })

      setSessions(response.sessions || [])
      setTotalPages(response.pagination.total_pages)

      // Auto-select first session if none selected
      if (!selectedSession && response.sessions && response.sessions.length > 0) {
        setSelectedSession(response.sessions[0])
      }

      // If current selected session exists in new data, update it
      if (selectedSession && response.sessions) {
        const updatedSession = response.sessions.find(
          s => s.session_id === selectedSession.session_id
        )
        if (updatedSession) {
          setSelectedSession(updatedSession)
        }
      }
    } catch (err: any) {
      console.error('Failed to fetch sessions:', err)
      if (!silent) {
        setError(err.message || 'Mesajlar yüklenirken hata oluştu')
      }
    } finally {
      if (!silent) {
        setIsLoading(false)
      }
    }
  }

  // Loading Skeleton Component
  const LoadingSkeleton = () => (
    <div className="flex-1 p-2 sm:p-3 lg:p-4 flex flex-col gap-2">
      {[1, 2, 3, 4, 5].map((i) => (
        <div
          key={i}
          className="h-20 bg-gray-100 rounded-lg animate-pulse"
        />
      ))}
    </div>
  )

  // Empty State Component
  const EmptyState = () => (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
          <User className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Henüz Mesajlaşma Yok
        </h3>
        <p className="text-sm text-gray-500">
          Bu chatbox ile henüz hiç mesajlaşma yapılmamış
        </p>
      </div>
    </div>
  )

  // Error State Component
  const ErrorState = () => (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="text-center max-w-md">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-50 flex items-center justify-center">
          <AlertCircle className="w-8 h-8 text-red-500" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Bir Hata Oluştu
        </h3>
        <p className="text-sm text-gray-500 mb-4">{error}</p>
        <button
          onClick={() => fetchSessions()}
          className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Tekrar Deneyin
        </button>
      </div>
    </div>
  )

  // No Chatbox Selected State
  if (!selectedChatbox) {
    return (
      <div className="flex flex-col lg:flex-row gap-4 lg:gap-8 w-full mt-4 lg:mt-8 px-2 sm:px-4">
        <div className="bg-white border-2 border-gray-200 rounded-2xl flex items-center justify-center w-full h-[600px] lg:h-[700px]">
          <div className="text-center p-8">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
              <Bot className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Chatbox Seçin
            </h3>
            <p className="text-sm text-gray-500">
              Mesajlaşma kayıtlarını görmek için bir chatbox seçin
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col lg:flex-row gap-4 lg:gap-8 w-full mt-4 lg:mt-8 px-2 sm:px-4">
      {/* Session List (Left Panel) */}
      <div
        className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out translate-y-0 scale-100 w-full lg:w-1/4 h-[600px] lg:h-[700px]"
        style={{
          borderColor: selectedChatbox?.primary_color || '#E5E7EB',
          animationDelay: '150ms',
          transition: 'border-color 300ms ease-in-out'
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 sm:p-6 lg:p-8 border-b border-gray-200">
          <h3 className="text-xl sm:text-2xl lg:text-3xl">
            <span
              className="font-bold bg-gradient-to-r bg-clip-text text-transparent"
              style={{
                backgroundImage: selectedChatbox
                  ? `linear-gradient(135deg, ${selectedChatbox.primary_color}, ${selectedChatbox.button_primary_color})`
                  : `linear-gradient(135deg, ${themeColors.primary}, ${themeColors.secondary})`
              }}
            >
              Mesajlar
            </span>
          </h3>
          {isLoading && (
            <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
          )}
        </div>

        {/* Content */}
        {isLoading && sessions.length === 0 ? (
          <LoadingSkeleton />
        ) : error ? (
          <ErrorState />
        ) : sessions.length === 0 ? (
          <EmptyState />
        ) : (
          <>
            <div className="flex-1 p-2 sm:p-3 lg:p-4 flex flex-col overflow-y-auto gap-2">
              {sessions.map((session) => (
                <div
                  key={session.session_id}
                  onClick={() => setSelectedSession(session)}
                  className={`p-3 sm:p-4 rounded-lg cursor-pointer transition-all duration-200 border ${
                    selectedSession?.session_id === session.session_id
                      ? 'border-2 shadow-md'
                      : 'border border-gray-200 hover:border-gray-300 hover:shadow-sm'
                  }`}
                  style={{
                    borderColor:
                      selectedSession?.session_id === session.session_id
                        ? selectedChatbox?.primary_color || themeColors.primary
                        : undefined,
                    backgroundColor:
                      selectedSession?.session_id === session.session_id
                        ? `${selectedChatbox?.primary_color || themeColors.primary}08`
                        : 'white',
                    transition: 'all 300ms ease-in-out'
                  }}
                >
                  <div className="flex items-start space-x-2 sm:space-x-3">
                    <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm sm:text-base font-semibold text-gray-900 truncate">
                        {getSessionDisplayName(session.ziyaretci_id)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatMessageDate(session.first_message_at)}
                      </p>
                      <p className="text-xs sm:text-sm text-gray-600 mt-1 line-clamp-2">
                        {getFirstUserMessage(session.messages)}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {session.message_count} mesaj
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="border-t border-gray-200 p-4 flex justify-between items-center">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Önceki
                </button>
                <span className="text-sm text-gray-600">
                  {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Sonraki
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Message Details (Right Panel) */}
      <div
        className="bg-white border-2 rounded-2xl flex flex-col transition-all duration-700 ease-out translate-y-0 scale-100 w-full lg:w-3/4 h-[600px] lg:h-[700px]"
        style={{
          borderColor: selectedChatbox?.primary_color || '#E5E7EB',
          animationDelay: '300ms',
          transition: 'border-color 300ms ease-in-out'
        }}
      >
        {selectedSession ? (
          <>
            {/* Header */}
            <div className="flex items-center p-4 sm:p-6 lg:p-8 border-b border-gray-200">
              <div className="flex items-center space-x-3 flex-1">
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-gray-200 flex items-center justify-center">
                  <User className="w-5 h-5 sm:w-6 sm:h-6 text-gray-600" />
                </div>
                <div>
                  <h3 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900">
                    {getSessionDisplayName(selectedSession.ziyaretci_id)}
                  </h3>
                  <p className="text-xs sm:text-sm text-gray-500">
                    {formatMessageDate(selectedSession.first_message_at)}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500">
                  {selectedSession.message_count} mesaj
                </p>
                {selectedSession.avg_response_time_ms && (
                  <p className="text-xs text-gray-400">
                    Ort. yanıt: {Math.round(selectedSession.avg_response_time_ms / 1000)}s
                  </p>
                )}
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 p-4 sm:p-6 lg:p-8 flex flex-col overflow-y-auto space-y-4">
              {selectedSession.messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.message_direction === 'incoming' ? 'justify-start' : 'justify-end'
                  }`}
                >
                  <div
                    className="max-w-[75%] sm:max-w-[70%] rounded-2xl px-4 py-3 transition-colors duration-300"
                    style={{
                      backgroundColor:
                        message.message_direction === 'incoming'
                          ? selectedChatbox?.user_message_color || '#F3F4F6'
                          : selectedChatbox?.ai_message_color || '#E5E7EB',
                      color:
                        message.message_direction === 'incoming'
                          ? selectedChatbox?.user_text_color || '#1F2937'
                          : selectedChatbox?.ai_text_color || '#1F2937'
                    }}
                  >
                    <div className="flex items-start space-x-2">
                      {message.message_direction === 'outgoing' && (
                        <Bot className="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <p className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap">
                          {message.content}
                        </p>
                        <p className="text-xs mt-1 opacity-75">
                          {formatMessageTime(message.created_at)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center p-8">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
                <Bot className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Bir konuşma seçin
              </h3>
              <p className="text-sm text-gray-500">
                Mesajları görmek için sol taraftan bir konuşma seçin
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
