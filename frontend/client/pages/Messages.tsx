import { useState } from "react";
import { Send, Search, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Message {
  id: string;
  sender: "user" | "other";
  text: string;
  timestamp: Date;
}

interface Conversation {
  id: string;
  contactName: string;
  contactAvatar: string;
  lastMessage: string;
  lastMessageTime: Date;
  messages: Message[];
}

const mockConversations: Conversation[] = [
  {
    id: "1",
    contactName: "Sarah M.",
    contactAvatar: "S",
    lastMessage: "Thank you for the book! It's in great condition.",
    lastMessageTime: new Date(Date.now() - 2 * 60 * 60 * 1000),
    messages: [
      {
        id: "1",
        sender: "other",
        text: "Hi! I'm interested in The Great Gatsby",
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
      },
      {
        id: "2",
        sender: "user",
        text: "Hey! Yes, it's available. It's in great condition.",
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000 + 5 * 60 * 1000),
      },
      {
        id: "3",
        sender: "other",
        text: "Perfect! When can we exchange?",
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000 + 10 * 60 * 1000),
      },
      {
        id: "4",
        sender: "user",
        text: "How about this weekend?",
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000 + 15 * 60 * 1000),
      },
      {
        id: "5",
        sender: "other",
        text: "Thank you for the book! It's in great condition.",
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
      },
    ],
  },
  {
    id: "2",
    contactName: "Emma T.",
    contactAvatar: "E",
    lastMessage: "Sounds good!",
    lastMessageTime: new Date(Date.now() - 5 * 60 * 60 * 1000),
    messages: [
      {
        id: "1",
        sender: "other",
        text: "Do you have any mystery books?",
        timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000),
      },
      {
        id: "2",
        sender: "user",
        text: "I have 1984 by George Orwell. It's excellent.",
        timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000 + 3 * 60 * 1000),
      },
      {
        id: "3",
        sender: "other",
        text: "Sounds good!",
        timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000),
      },
    ],
  },
  {
    id: "3",
    contactName: "John D.",
    contactAvatar: "J",
    lastMessage: "Let's meet next Tuesday",
    lastMessageTime: new Date(Date.now() - 12 * 60 * 60 * 1000),
    messages: [
      {
        id: "1",
        sender: "other",
        text: "I'm interested in To Kill a Mockingbird",
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
      },
      {
        id: "2",
        sender: "user",
        text: "Yes, I have it available!",
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000 + 10 * 60 * 1000),
      },
      {
        id: "3",
        sender: "other",
        text: "Let's meet next Tuesday",
        timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000),
      },
    ],
  },
];

function formatTime(date: Date) {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 60) {
    return `${minutes}m ago`;
  } else if (hours < 24) {
    return `${hours}h ago`;
  } else if (days === 1) {
    return "Yesterday";
  } else {
    return date.toLocaleDateString();
  }
}

export default function Messages() {
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(
    mockConversations[0]
  );
  const [messageInput, setMessageInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [isMobileViewChat, setIsMobileViewChat] = useState(false);

  const filteredConversations = mockConversations.filter((conv) =>
    conv.contactName.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSendMessage = () => {
    if (!messageInput.trim() || !selectedConversation) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: messageInput,
      timestamp: new Date(),
    };

    setSelectedConversation({
      ...selectedConversation,
      messages: [...selectedConversation.messages, newMessage],
      lastMessage: messageInput,
      lastMessageTime: new Date(),
    });

    setMessageInput("");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <main className="container mx-auto px-0 sm:px-8 h-screen flex flex-col py-0 sm:py-6">
        {/* Header - Hidden on mobile when in chat view */}
        {!isMobileViewChat && (
          <div className="hidden sm:flex flex-col gap-2 mb-6 px-4 sm:px-0">
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900">Messages</h1>
            <p className="text-gray-600">Connect and exchange with the community</p>
          </div>
        )}

        <div className="flex-1 flex gap-0 sm:gap-6 min-h-0 rounded-xl overflow-hidden sm:overflow-visible">
          {/* Left Sidebar - Conversations List */}
          {!isMobileViewChat && (
            <div className="w-full sm:w-96 bg-white rounded-none sm:rounded-xl shadow-sm flex flex-col overflow-hidden">
              {/* Search Bar */}
              <div className="p-4 border-b border-gray-200">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search conversations..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6750A4] text-sm"
                  />
                </div>
              </div>

              {/* Conversations List */}
              <div className="flex-1 overflow-y-auto">
                {filteredConversations.length === 0 ? (
                  <div className="p-4 text-center text-gray-600 text-sm">
                    No conversations found
                  </div>
                ) : (
                  <div className="space-y-2 p-2">
                    {filteredConversations.map((conversation) => (
                      <button
                        key={conversation.id}
                        onClick={() => {
                          setSelectedConversation(conversation);
                          setIsMobileViewChat(true);
                        }}
                        className={`w-full p-3 rounded-lg text-left hover:bg-gray-50 transition-colors ${
                          selectedConversation?.id === conversation.id
                            ? "bg-[#F3E5F5] border-l-4 border-[#6750A4]"
                            : "border-l-4 border-transparent"
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          {/* Avatar */}
                          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-blue-500 flex items-center justify-center text-white font-semibold flex-shrink-0 text-sm">
                            {conversation.contactAvatar}
                          </div>

                          {/* Conversation Info */}
                          <div className="flex-1 min-w-0">
                            <h3 className="font-semibold text-gray-900 text-sm">
                              {conversation.contactName}
                            </h3>
                            <p className="text-xs text-gray-600 line-clamp-1">
                              {conversation.lastMessage}
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                              {formatTime(conversation.lastMessageTime)}
                            </p>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Right Chat Area */}
          {selectedConversation ? (
            <div
              className={`${
                isMobileViewChat ? "w-full" : "hidden sm:flex"
              } flex-1 flex flex-col bg-white rounded-none sm:rounded-xl shadow-sm overflow-hidden`}
            >
              {/* Chat Header */}
              <div className="p-4 sm:p-6 border-b border-gray-200 flex items-center gap-4 bg-gradient-to-r from-white to-gray-50">
                {isMobileViewChat && (
                  <button
                    onClick={() => setIsMobileViewChat(false)}
                    className="sm:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <ArrowLeft className="w-5 h-5 text-gray-900" />
                  </button>
                )}
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-blue-500 flex items-center justify-center text-white font-semibold">
                  {selectedConversation.contactAvatar}
                </div>
                <div className="flex-1">
                  <h2 className="font-semibold text-gray-900">
                    {selectedConversation.contactName}
                  </h2>
                  <p className="text-sm text-green-600 font-medium">Active now</p>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
                {selectedConversation.messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.sender === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                        message.sender === "user"
                          ? "bg-[#6750A4] text-white rounded-br-none shadow-sm"
                          : "bg-gray-100 text-gray-900 rounded-bl-none"
                      }`}
                    >
                      <p className="text-sm sm:text-base leading-relaxed">
                        {message.text}
                      </p>
                      <p
                        className={`text-xs mt-2 ${
                          message.sender === "user"
                            ? "text-purple-100"
                            : "text-gray-500"
                        }`}
                      >
                        {message.timestamp.toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Message Input */}
              <div className="p-4 sm:p-6 border-t border-gray-200 bg-gray-50">
                <div className="flex gap-2 sm:gap-3">
                  <input
                    type="text"
                    placeholder="Write a message..."
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === "Enter") {
                        handleSendMessage();
                      }
                    }}
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-[#6750A4] text-sm"
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!messageInput.trim()}
                    className="bg-[#6750A4] hover:bg-[#5a4494] text-white font-semibold p-3 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    <Send className="w-5 h-5" />
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="hidden sm:flex flex-1 bg-white rounded-xl shadow-sm items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
                  <MessageCircleIcon className="w-8 h-8 text-gray-400" />
                </div>
                <p className="text-gray-600">Select a conversation to start chatting</p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function MessageCircleIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
    </svg>
  );
}
