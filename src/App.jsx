import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import ChatArea from './components/ChatArea'
import ApiService from './services/api'
import './App.css'

function App() {
  const [chats, setChats] = useState([])
  const [currentChatId, setCurrentChatId] = useState(null)
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  // تحميل المحادثات عند بدء التطبيق
  useEffect(() => {
    console.log('App mounted, loading chats...')
    loadChats()
  }, [])

  // تحميل رسائل المحادثة الحالية
  useEffect(() => {
    console.log('Current chat ID changed:', currentChatId)
    if (currentChatId) {
      loadChatMessages(currentChatId)
    } else {
      setMessages([])
    }
  }, [currentChatId])

  const loadChats = async () => {
    try {
      console.log('Loading chats...')
      const response = await ApiService.getChats()
      console.log('Chats response:', response)
      if (response.success) {
        setChats(response.chats)
        console.log('Chats loaded:', response.chats)
      }
    } catch (error) {
      console.error('خطأ في تحميل المحادثات:', error)
      setError('فشل في تحميل المحادثات')
    }
  }

  const loadChatMessages = async (chatId) => {
    try {
      console.log('Loading messages for chat:', chatId)
      const response = await ApiService.getChat(chatId)
      console.log('Messages response:', response)
      if (response.success) {
        setMessages(response.messages)
        console.log('Messages loaded:', response.messages)
      }
    } catch (error) {
      console.error('خطأ في تحميل الرسائل:', error)
      setError('فشل في تحميل الرسائل')
    }
  }

  const handleNewChat = async () => {
    try {
      console.log('Creating new chat...')
      const response = await ApiService.createChat()
      console.log('New chat response:', response)
      if (response.success) {
        const newChat = response.chat
        setChats(prev => [newChat, ...prev])
        setCurrentChatId(newChat.id)
        setMessages([])
      }
    } catch (error) {
      console.error('خطأ في إنشاء محادثة جديدة:', error)
      setError('فشل في إنشاء محادثة جديدة')
    }
  }

  const handleChatSelect = (chatId) => {
    console.log('Chat selected:', chatId)
    setCurrentChatId(chatId)
  }

  const handleDeleteChat = async (chatId) => {
    try {
      const response = await ApiService.deleteChat(chatId)
      if (response.success) {
        setChats(prev => prev.filter(chat => chat.id !== chatId))
        if (currentChatId === chatId) {
          setCurrentChatId(null)
          setMessages([])
        }
      }
    } catch (error) {
      console.error('خطأ في حذف المحادثة:', error)
      setError('فشل في حذف المحادثة')
    }
  }

  const handleSendMessage = async (messageContent) => {
    if (!currentChatId) {
      // إنشاء محادثة جديدة إذا لم تكن موجودة
      await handleNewChat()
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      console.log('Sending message:', messageContent, 'to chat:', currentChatId)
      const response = await ApiService.sendMessage(currentChatId, messageContent)
      console.log('Send message response:', response)
      
      if (response.success) {
        // إضافة الرسائل الجديدة
        setMessages(prev => [
          ...prev,
          response.user_message,
          response.assistant_message
        ])
        
        // تحديث قائمة المحادثات
        await loadChats()
      } else {
        // في حالة فشل الذكاء الاصطناعي، أضف رسالة المستخدم فقط
        if (response.user_message) {
          setMessages(prev => [...prev, response.user_message])
        }
        setError(response.error || 'فشل في معالجة الرسالة')
      }
    } catch (error) {
      console.error('خطأ في إرسال الرسالة:', error)
      setError('فشل في إرسال الرسالة')
    } finally {
      setIsLoading(false)
    }
  }

  const handleHome = () => {
    setCurrentChatId(null)
    setMessages([])
  }

  console.log('App render - chats:', chats.length, 'currentChatId:', currentChatId, 'messages:', messages.length)

  return (
    <div className="flex h-screen bg-background text-foreground" dir="rtl">
      <Sidebar
        chats={chats}
        currentChatId={currentChatId}
        onChatSelect={handleChatSelect}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        onHome={handleHome}
      />
      
      <div className="flex-1 flex flex-col">
        {error && (
          <div className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-2 text-sm">
            {error}
            <button 
              onClick={() => setError(null)}
              className="float-left text-destructive hover:text-destructive/80"
            >
              ✕
            </button>
          </div>
        )}
        
        <ChatArea
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          currentChatId={currentChatId}
        />
      </div>
    </div>
  )
}

export default App
