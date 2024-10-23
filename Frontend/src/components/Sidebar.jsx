import React from 'react';
import './Sidebar.css';
import newChatIcon from '../assets/newchat.png'

const Sidebar = ({ chatItems, onChatItemClick, onNewChat }) => {
  const getStatusColor = (status) => {
    const statusColors = {
      completed: "status-completed",
      active: "status-active",
      pending: "status-pending"
    };
    return statusColors[status] || "";
  };

  return (
    <aside className="sidebar">
      <nav className="sidebar-nav"> 
        {/* New Chat Button */}
        <div className="new-chat-btn-container">
          <button className='new-chat-btn' onClick={onNewChat}>
            <img src={newChatIcon} alt="New Chat" className='new-chat-icon'/>
          </button>
        </div>
        <div className="history-box">
          {chatItems.map((chat) => (
            <div 
              key={chat.id} 
              className="chat-history-item"
              onClick={() => onChatItemClick(chat)}  // Call the click handler
            >
              <div className="chat-header">
                <div className="chat-title-container">
                  <div className={`status-dot ${getStatusColor(chat.status)}`}></div>
                  <h3 className="chat-title">{chat.title}</h3>
                </div>
                <div className="chat-meta">
                  <span className="chat-time">{chat.time}</span>
                </div>
              </div>
              
              <div className="chat-body">
                <p className="chat-summary">{chat.summary}</p>
              </div>
            </div>
          ))}
        </div>
      </nav>
    </aside>
  );
};

export default Sidebar;
