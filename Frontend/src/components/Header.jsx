import React, { useState } from 'react';
import headerStyles from './Header.css'; // Assuming you create a CSS file for styling
import logoicon from '../assets/logo.png'
import homeIcon from '../assets/home.png';
import refreshIcon from '../assets/dashboard.png';
import chatIcon from '../assets/chat.png';
import notebookIcon from '../assets/notebook.png';
import logo from '../assets/logo.png';
import userAvatar from '../assets/profile_picture.png';
import { Home, Clock, MessageCircle, Menu } from 'lucide-react';

// Header.jsx

const ChatHeader = () => {
  const [activeTab, setActiveTab] = useState('chat');

  const navItems = [
    { id: 'home', icon: homeIcon, label: 'Home' },
    { id: 'history', icon: refreshIcon, label: 'History' },
    { id: 'chat', icon: chatIcon, label: 'Chat' },
    { id: 'menu', icon: notebookIcon, label: 'Menu' }
  ];

  return (
    <div className="header-container">
       <img src={logo} alt="Logo" className="logo" />
      <nav className="nav-container">
        {navItems.map(({ id, icon, label }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`nav-button ${activeTab === id ? 'active' : ''}`}
            aria-label={label}
          >
            <img src={icon} alt={label} className="nav-icon" />
          </button>
        ))}
      </nav>
    </div>
  );
};

export default ChatHeader;

