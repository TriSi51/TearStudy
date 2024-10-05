import React from 'react';
import Message from './Message';

function ChatMessages({ messages }) {
  return (
    <div className="chat-messages">
      {messages.map((msg) => (
        <Message key={msg.id} text={msg.text} sender={msg.sender} />
      ))}
    </div>
  );
}

export default ChatMessages;