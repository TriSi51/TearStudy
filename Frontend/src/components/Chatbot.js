import React, { useState } from 'react';
import axios from 'axios'; // Import Axios for making HTTP requests
import ChatMessages from './ChatMessages';
import ChatInput from './ChatInput';
import MultipleFileUpload from './FileHandle';
function Chatbot() {
  const [messages, setMessages] = useState([
    { id: 1, text: 'Hello! How can I help you today?', sender: 'bot' },
  ]);

  const handleSendMessage = async(message) => {
    setMessages([...messages, { id: messages.length + 1, text: message, sender: 'user' }]);
    
    try{
      //send user message to backend
      const response= await axios.post('http://127.0.0.1:8000/api/chat',{
        message: message,
      });

      //add bot response
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          id:messages.length +1 ,text: response.data.response, sender: 'bot'
        },
      ]);



    }
    catch (error){
        setMessages((prevMessages)=>[
          ...prevMessages,
          {
            id:message.length+1,text: 'Error: Could not reach server.',sender:'bot'
          },
        ]);
    }

  };

  return (
    <div className="chatbot">
      <ChatMessages messages={messages} />
      <ChatInput onSendMessage={handleSendMessage} />
      <MultipleFileUpload multiplefile={[]}/>
    </div>
  );
}

export default Chatbot;