import React, { useState } from "react";
import ChatHeader from './Header';
import Sidebar from './Sidebar';
import ChatArea from './ChatArea';
import './style.css';

const ChatScreen = () => {
  const initialChatItems = [
    {
      id: 1,
      title: "Project Discussion with Design Team",
      summary: "Discussed UI improvements and new features",
      date: "2024-10-23",
      time: "10:30 AM",
      participants: ["Alex", "Maria", "John"],
      messages: [
        { id: 1, text: "Hey team, let's discuss the UI improvements.", isBot: false },
        { id: 2, text: "Sure, here's a draft with new features.", isBot: true },
      ],
      status: "completed"
    },
    {
      id: 2,
      title: "Client Meeting - Website Redesign",
      summary: "Reviewed initial mockups and feedback",
      date: "2024-10-23",
      time: "2:15 PM",
      participants: ["Sarah", "Client Team"],
      messages: [
        { id: 1, text: "Client feedback on the redesign?", isBot: false },
        { id: 2, text: "The client mentioned a few changes for the mockups.", isBot: true },
      ],
      status: "active"
    }
  ];

  const [chatItems, setChatItems] = useState(initialChatItems);
  const [selectedChat, setSelectedChat] = useState(initialChatItems[0]);
  const [animationClass, setAnimationClass] = useState("slide-in");

  // Function to handle new chat creation
  const handleNewChat = () => {
    const newChat = {
      id: chatItems.length + 1,
      title: "New Chat",
      summary: "Start your conversation...",
      date: new Date().toISOString().split("T")[0],
      time: new Date().toLocaleTimeString(),
      participants: ["You"],
      messages: [
        { id: 1, text: "Welcome to your new chat!", isBot: true },
      ],
      status: "active"
    };

    // Add the new chat to the list
    setChatItems([newChat, ...chatItems]);

    // Automatically select the new chat
    setSelectedChat(newChat);
  };

  const handleChatItemClick = (chat) => {
    setAnimationClass("slide-out"); // Trigger slide-out before updating chat

    setTimeout(() => {
      setSelectedChat(chat);
      setAnimationClass("slide-in"); // Slide in the new chat
    }, 3000); // 3-second timeout matching the CSS transition time
  };

  return (
    <div className="chat-skeleton">
      {/* Top Header */}
      <ChatHeader />

      {/* Main Content */}
      <div className="content-area">
        {/* Sidebar */}
        <Sidebar chatItems={chatItems} onChatItemClick={handleChatItemClick} onNewChat={handleNewChat} />

        {/* Chat Area with smooth animation */}
        <div className={`chat-area ${animationClass}`}>
          <ChatArea messages={selectedChat.messages} />
        </div>
      </div>
    </div>
  );
};

export default ChatScreen;
