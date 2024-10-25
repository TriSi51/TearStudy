import React, { useState } from 'react';
import { Send } from 'lucide-react';
import axios from 'axios'; 
import './ChatArea.css';
import userAvatar from '../assets/avatar.png'; 
import botAvatar from '../assets/bot.png';

const ChatArea = ({ messages }) => {
  const [inputValue, setInputValue] = useState('');
  const [localMessages, setLocalMessages] = useState([]);


  const combinedMessages = [...messages, ...localMessages];


  const handleSubmit = async(e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    // Handle message submission logic
    


  const newMessage = {
    id: combinedMessages.length + 1,  // Incremental ID
    text: inputValue,                 // Message input value
    isBot: false,                     // Message is from the user
  };

  setLocalMessages([...localMessages, newMessage]);  // Update localMessages with new message
  setInputValue('');  // Clear the input field after submission
  try {
    const response= await axios.post('http://127.0.0.1:8000/message', {
      message: newMessage.text,
    });
    console.log('Response from backend:', response.data.message.response);
    const botMessage = response.data.message.response
    setLocalMessages((prevMessages) => [
      ...prevMessages,
      {
        id:localMessages.length +1 ,text: botMessage, isBot: true
      },
    ]);   
  }
  catch(error){
    setLocalMessages((prevMessages) => [
      ...prevMessages,
      {
        id:localMessages.length+1,text: 'Error: Could not reach server',isBot: true
      }
    ])
  }

};

  return (
    <div className="chat-container">
      <div className="messages-area">
        <div className="messages-wrapper">
          {combinedMessages.map((message) => (
            <div
              key={message.id}
              className={`message-row ${message.isBot ? 'bot-message' : 'user-message'}`}
            >
              {message.isBot && (
                <div className="avatar bot-avatar">
                  <img src={botAvatar} alt="Bot" />
                </div>
              )}
              <div className="message-bubble">
                <p>{message.text}</p>
              </div>
              {!message.isBot && (
                <div className="avatar user-avatar">
                  <img src={userAvatar} alt="User" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="input-area">
        <div className="input-wrapper">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type a message..."
          />
          <button type="submit">
            <Send size={20} />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatArea;
