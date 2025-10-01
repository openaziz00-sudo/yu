import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  MessageCircle, 
  Plus, 
  Home, 
  Settings, 
  Trash2,
  Bot
} from 'lucide-react'

const Sidebar = ({ 
  chats, 
  currentChatId, 
  onChatSelect, 
  onNewChat, 
  onDeleteChat,
  onHome 
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false)

  return (
    <div className={`bg-sidebar border-r border-sidebar-border transition-all duration-300 ${
      isCollapsed ? 'w-16' : 'w-80'
    } flex flex-col h-screen`}>
      {/* Header */}
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-6 h-6 text-sidebar-primary" />
            {!isCollapsed && (
              <h1 className="text-lg font-semibold text-sidebar-foreground">
                Gentle AI
              </h1>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="text-sidebar-foreground hover:bg-sidebar-accent"
          >
            <MessageCircle className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Navigation */}
      <div className="p-4 space-y-2">
        <Button
          onClick={onNewChat}
          className="w-full justify-start gap-2 bg-sidebar-primary hover:bg-sidebar-primary/90 text-sidebar-primary-foreground"
        >
          <Plus className="w-4 h-4" />
          {!isCollapsed && 'محادثة جديدة'}
        </Button>
        
        <Button
          onClick={onHome}
          variant="ghost"
          className="w-full justify-start gap-2 text-sidebar-foreground hover:bg-sidebar-accent"
        >
          <Home className="w-4 h-4" />
          {!isCollapsed && 'الرئيسية'}
        </Button>
      </div>

      {/* Chat History */}
      {!isCollapsed && (
        <div className="flex-1 flex flex-col min-h-0">
          <div className="px-4 py-2">
            <h2 className="text-sm font-medium text-sidebar-foreground/70">
              المحادثات السابقة
            </h2>
          </div>
          
          <ScrollArea className="flex-1 px-2">
            <div className="space-y-1">
              {chats.map((chat) => (
                <div
                  key={chat.id}
                  className={`group flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
                    currentChatId === chat.id
                      ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                      : 'hover:bg-sidebar-accent/50 text-sidebar-foreground'
                  }`}
                  onClick={() => onChatSelect(chat.id)}
                >
                  <MessageCircle className="w-4 h-4 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm truncate">{chat.title}</p>
                    <p className="text-xs text-sidebar-foreground/50">
                      {chat.message_count} رسالة
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteChat(chat.id)
                    }}
                    className="opacity-0 group-hover:opacity-100 transition-opacity p-1 h-auto w-auto text-sidebar-foreground/50 hover:text-destructive"
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      )}

      {/* Settings */}
      <div className="p-4 border-t border-sidebar-border">
        <Button
          variant="ghost"
          className="w-full justify-start gap-2 text-sidebar-foreground hover:bg-sidebar-accent"
        >
          <Settings className="w-4 h-4" />
          {!isCollapsed && 'الإعدادات'}
        </Button>
      </div>
    </div>
  )
}

export default Sidebar
