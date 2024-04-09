import React, { useContext, useState } from 'react';
import MyContext from '../../Context/Context';

const MessageDisplay = () => {
  const { conversations, selectConversation, currentMessages } = useContext(MyContext);
  const [selectedConversation, setSelectedConversation] = useState(null);

  const handleSelectConversation = (conversationId) => {
    selectConversation(conversationId);
    setSelectedConversation(conversationId);
  };

  return (
    <div style={{ position: 'fixed', bottom: '10px', right: '10px', width: '300px', height: '400px', overflow: 'auto', background: 'white' }}>
      <div>
        {conversations.map((conversation) => (
          <div key={conversation.id} onClick={() => handleSelectConversation(conversation.id)}>
            Conversation {conversation.id}
          </div>
        ))}
      </div>
      <div>
        {selectedConversation === null ? (
          <p>Select a conversation to view messages</p>
        ) : (
          currentMessages.map((message, index) => <div key={index}>{message.content}</div>)
        )}
      </div>
    </div>
  );
};

export default MessageDisplay;
