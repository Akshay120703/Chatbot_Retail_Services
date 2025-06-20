const Chat = ({ onProductSearch }) => {
    const [messages, setMessages] = React.useState([
        {
            id: 1,
            type: 'agent',
            content: "Hello! I'm your AI Shopping Agent. I can help you find products based on your needs. Just tell me what you're looking for!",
            timestamp: new Date()
        }
    ]);
    const [inputMessage, setInputMessage] = React.useState('');
    const [loading, setLoading] = React.useState(false);
    const messagesEndRef = React.useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    React.useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = async () => {
        if (!inputMessage.trim() || loading) return;

        const userMessage = {
            id: Date.now(),
            type: 'user',
            content: inputMessage,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setLoading(true);

        try {
            const response = await axios.post('/api/chat', {
                content: inputMessage
            });

            const agentMessage = {
                id: Date.now() + 1,
                type: 'agent',
                content: response.data.response,
                timestamp: new Date(),
                hasProducts: response.data.has_products,
                products: response.data.products,
                filterOptions: response.data.filter_options,
                filterName: response.data.filter_name
            };

            setMessages(prev => [...prev, agentMessage]);

            // If the response includes products, trigger the product search display
            if (response.data.has_products && response.data.products.length > 0) {
                onProductSearch({
                    query: inputMessage,
                    products: response.data.products,
                    explanation: response.data.response
                });
            }

        } catch (error) {
            console.error('Chat error:', error);
            const errorMessage = {
                id: Date.now() + 1,
                type: 'agent',
                content: "I'm sorry, I encountered an error processing your request. Please try again.",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const formatTime = (timestamp) => {
        return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return React.createElement('div', { className: 'chat-container' },
        // Chat Header
        React.createElement('div', { className: 'chat-header' },
            React.createElement('i', { className: 'fas fa-robot' }),
            React.createElement('span', null, 'AI Shopping Agent'),
            React.createElement('span', { className: 'ml-auto text-sm' }, 'Online')
        ),

        // Chat Messages
        React.createElement('div', { className: 'chat-messages' },
            ...messages.map(message =>
                React.createElement('div', {
                    key: message.id,
                    className: `message ${message.type}`
                },
                    React.createElement('div', { className: 'message-avatar' },
                        message.type === 'user' ? 'U' : React.createElement('i', { className: 'fas fa-robot' })
                    ),
                    React.createElement('div', { className: 'message-content' },
                        React.createElement('p', null, message.content),
                        message.hasProducts && React.createElement('p', { 
                            style: { marginTop: '0.5rem', fontSize: '0.9rem', opacity: 0.8 } 
                        }, `Found ${message.products.length} products - check below!`),
                        message.filterOptions && message.filterOptions.length > 0 && React.createElement('div', {
                            style: { marginTop: '1rem' }
                        },
                            React.createElement('div', {
                                style: { 
                                    display: 'flex', 
                                    flexWrap: 'wrap', 
                                    gap: '0.5rem',
                                    marginTop: '0.5rem'
                                }
                            },
                                ...message.filterOptions.map(option =>
                                    React.createElement('button', {
                                        key: option,
                                        onClick: async () => {
                                            setInputMessage(option);
                                            // Automatically send the selected option
                                            const userMessage = {
                                                id: Date.now(),
                                                type: 'user',
                                                content: option,
                                                timestamp: new Date()
                                            };
                                            
                                            setMessages(prev => [...prev, userMessage]);
                                            setLoading(true);
                                            
                                            try {
                                                const response = await axios.post('/api/chat', {
                                                    content: option
                                                });
                                                
                                                const agentMessage = {
                                                    id: Date.now() + 1,
                                                    type: 'agent',
                                                    content: response.data.response,
                                                    timestamp: new Date(),
                                                    hasProducts: response.data.has_products,
                                                    products: response.data.products,
                                                    filterOptions: response.data.filter_options,
                                                    filterName: response.data.filter_name
                                                };
                                                
                                                setMessages(prev => [...prev, agentMessage]);
                                                
                                                if (response.data.has_products && response.data.products.length > 0) {
                                                    onProductSearch({
                                                        query: option,
                                                        products: response.data.products,
                                                        explanation: response.data.response
                                                    });
                                                }
                                            } catch (error) {
                                                console.error('Chat error:', error);
                                                const errorMessage = {
                                                    id: Date.now() + 1,
                                                    type: 'agent',
                                                    content: "I'm sorry, I encountered an error processing your request. Please try again.",
                                                    timestamp: new Date()
                                                };
                                                setMessages(prev => [...prev, errorMessage]);
                                            } finally {
                                                setLoading(false);
                                            }
                                        },
                                        style: {
                                            background: '#FF6B35',
                                            color: 'white',
                                            border: 'none',
                                            padding: '0.25rem 0.75rem',
                                            borderRadius: '15px',
                                            cursor: 'pointer',
                                            fontSize: '0.85rem',
                                            transition: 'background-color 0.3s ease'
                                        },
                                        onMouseEnter: (e) => {
                                            e.target.style.background = '#E55A2B';
                                        },
                                        onMouseLeave: (e) => {
                                            e.target.style.background = '#FF6B35';
                                        }
                                    }, option)
                                )
                            )
                        ),
                        React.createElement('div', { 
                            style: { fontSize: '0.75rem', opacity: 0.7, marginTop: '0.25rem' } 
                        }, formatTime(message.timestamp))
                    )
                )
            ),
            loading && React.createElement('div', { className: 'message agent' },
                React.createElement('div', { className: 'message-avatar' },
                    React.createElement('i', { className: 'fas fa-robot' })
                ),
                React.createElement('div', { className: 'message-content' },
                    React.createElement('div', { className: 'loading' },
                        React.createElement('div', { className: 'spinner' }),
                        React.createElement('span', null, 'Thinking...')
                    )
                )
            ),
            React.createElement('div', { ref: messagesEndRef })
        ),

        // Chat Input
        React.createElement('div', { className: 'chat-input-container' },
            React.createElement('input', {
                type: 'text',
                className: 'chat-input',
                placeholder: 'Ask me to find products for you...',
                value: inputMessage,
                onChange: (e) => setInputMessage(e.target.value),
                onKeyPress: handleKeyPress,
                disabled: loading
            }),
            React.createElement('button', {
                className: 'chat-send-button',
                onClick: handleSendMessage,
                disabled: loading || !inputMessage.trim()
            },
                loading 
                    ? React.createElement('i', { className: 'fas fa-spinner fa-spin' })
                    : React.createElement('i', { className: 'fas fa-paper-plane' })
            )
        )
    );
};

window.Chat = Chat;
