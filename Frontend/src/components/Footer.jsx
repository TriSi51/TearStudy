import React from 'react';

const Footer = () => {
  return (
    <div className="chat-input">
      <input type="text" placeholder="..." />
      <button className="attachment-button"><img src="assets/attachment.png" alt="Attachment" /></button>
    </div>
  );
};

export default Footer;