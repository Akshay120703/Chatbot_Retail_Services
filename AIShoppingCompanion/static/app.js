const App = () => {
    const [searchQuery, setSearchQuery] = React.useState('');
    const [searchResults, setSearchResults] = React.useState(null);
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState(null);
    const [activeTab, setActiveTab] = React.useState('search');

    const handleSearch = async (query = searchQuery) => {
        if (!query.trim()) return;

        setLoading(true);
        setError(null);

        try {
            const response = await axios.post('/api/search', {
                query: query.trim()
            });

            setSearchResults(response.data);
            setActiveTab('results');
        } catch (err) {
            console.error('Search error:', err);
            setError(err.response?.data?.detail || 'Search failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleChatProductSearch = (results) => {
        setSearchResults(results);
        setActiveTab('results');
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    return React.createElement('div', { className: 'app' },
        // Header
        React.createElement('header', { className: 'header' },
            React.createElement('div', { className: 'header-content' },
                React.createElement('div', { className: 'logo' },
                    React.createElement('i', { className: 'fas fa-shopping-cart' }),
                    React.createElement('span', null, 'AI Shopping Agent')
                ),
                React.createElement('nav', null,
                    React.createElement('button', {
                        className: `nav-button ${activeTab === 'search' ? 'active' : ''}`,
                        onClick: () => setActiveTab('search'),
                        style: {
                            background: activeTab === 'search' ? 'rgba(255,255,255,0.2)' : 'transparent',
                            color: 'white',
                            border: '1px solid rgba(255,255,255,0.3)',
                            padding: '0.5rem 1rem',
                            borderRadius: '6px',
                            marginRight: '0.5rem',
                            cursor: 'pointer'
                        }
                    }, 'Search'),
                    React.createElement('button', {
                        className: `nav-button ${activeTab === 'chat' ? 'active' : ''}`,
                        onClick: () => setActiveTab('chat'),
                        style: {
                            background: activeTab === 'chat' ? 'rgba(255,255,255,0.2)' : 'transparent',
                            color: 'white',
                            border: '1px solid rgba(255,255,255,0.3)',
                            padding: '0.5rem 1rem',
                            borderRadius: '6px',
                            cursor: 'pointer'
                        }
                    }, 'Chat')
                )
            )
        ),

        // Main Content
        React.createElement('main', { className: 'main-content' },
            // Search Tab
            activeTab === 'search' && React.createElement('div', null,
                React.createElement('section', { className: 'search-section' },
                    React.createElement('h1', { className: 'search-title' }, 'Find Products with AI'),
                    React.createElement('p', { className: 'search-subtitle' },
                        'Tell me what you\'re looking for in natural language'
                    ),
                    React.createElement('div', { className: 'search-container' },
                        React.createElement('input', {
                            type: 'text',
                            className: 'search-input',
                            placeholder: 'e.g., "I need a smartphone under ₹20000 with good camera"',
                            value: searchQuery,
                            onChange: (e) => setSearchQuery(e.target.value),
                            onKeyPress: handleKeyPress,
                            disabled: loading
                        }),
                        React.createElement('button', {
                            className: 'search-button',
                            onClick: () => handleSearch(),
                            disabled: loading || !searchQuery.trim()
                        },
                            loading 
                                ? React.createElement('i', { className: 'fas fa-spinner fa-spin' })
                                : React.createElement('i', { className: 'fas fa-search' })
                        )
                    )
                ),

                // Sample Queries
                React.createElement('div', { 
                    style: { 
                        textAlign: 'center', 
                        marginBottom: '2rem',
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: '0.5rem',
                        justifyContent: 'center'
                    } 
                },
                    React.createElement('h3', { 
                        style: { 
                            width: '100%', 
                            marginBottom: '1rem',
                            color: '#6C757D',
                            fontSize: '1rem'
                        } 
                    }, 'Try these example searches:'),
                    ['Wireless headphones under ₹3000', 'Gaming laptop with RTX graphics', 'Smartwatch with fitness tracking'].map(query =>
                        React.createElement('button', {
                            key: query,
                            onClick: () => {
                                setSearchQuery(query);
                                handleSearch(query);
                            },
                            style: {
                                background: 'white',
                                border: '1px solid #DEE2E6',
                                padding: '0.5rem 1rem',
                                borderRadius: '20px',
                                cursor: 'pointer',
                                fontSize: '0.9rem',
                                transition: 'all 0.3s ease'
                            },
                            onMouseEnter: (e) => {
                                e.target.style.borderColor = '#FF6B35';
                                e.target.style.color = '#FF6B35';
                            },
                            onMouseLeave: (e) => {
                                e.target.style.borderColor = '#DEE2E6';
                                e.target.style.color = '#212529';
                            }
                        }, query)
                    )
                )
            ),

            // Chat Tab
            activeTab === 'chat' && React.createElement(window.Chat, {
                onProductSearch: handleChatProductSearch
            }),

            // Results Tab
            activeTab === 'results' && React.createElement(window.SearchResults, {
                results: searchResults,
                loading: loading,
                error: error
            })
        )
    );
};

// Initialize the app
const root = ReactDOM.createRoot ? ReactDOM.createRoot(document.getElementById('root')) : ReactDOM.render;
if (ReactDOM.createRoot) {
    root.render(React.createElement(App));
} else {
    ReactDOM.render(React.createElement(App), document.getElementById('root'));
}
