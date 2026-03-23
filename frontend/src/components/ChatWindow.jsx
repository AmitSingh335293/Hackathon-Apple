import React from 'react';

const ChatWindow = ({ messages }) => {
  return (
    <div className="chat-window">
      {messages.map((msg, idx) => (
        <div key={idx} className={msg.sender === 'user' ? 'user-message' : 'bot-message'}>
          {msg.text}
        </div>
      ))}
    </div>
  );
};

export default ChatWindow;
