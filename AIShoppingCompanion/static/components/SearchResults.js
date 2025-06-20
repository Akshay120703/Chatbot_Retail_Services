const SearchResults = ({ results, loading, error }) => {
    if (loading) {
        return React.createElement('div', { className: 'results-section' },
            React.createElement('div', { className: 'text-center' },
                React.createElement('div', { className: 'loading' },
                    React.createElement('div', { className: 'spinner' }),
                    React.createElement('span', null, 'Searching for products...')
                )
            )
        );
    }

    if (error) {
        return React.createElement('div', { className: 'results-section' },
            React.createElement('div', { className: 'error-message' },
                React.createElement('i', { className: 'fas fa-exclamation-triangle' }),
                ` ${error}`
            )
        );
    }

    if (!results || !results.products || results.products.length === 0) {
        return React.createElement('div', { className: 'empty-state' },
            React.createElement('i', { className: 'fas fa-search' }),
            React.createElement('h3', null, 'No products found'),
            React.createElement('p', null, 'Try adjusting your search criteria or use different keywords.')
        );
    }

    const sortedProducts = [...results.products].sort((a, b) => b.relevance_score - a.relevance_score);

    return React.createElement('div', { className: 'results-section' },
        // Results Header
        React.createElement('div', { className: 'results-header' },
            React.createElement('h2', { className: 'results-title' }, 'Product Recommendations'),
            React.createElement('span', { className: 'results-count' },
                `${results.products.length} products found`
            )
        ),

        // Search Explanation
        results.explanation && React.createElement('div', { className: 'explanation mb-4' },
            React.createElement('i', { className: 'fas fa-lightbulb' }),
            ` ${results.explanation}`
        ),

        // Products Grid
        React.createElement('div', { className: 'products-grid' },
            ...sortedProducts.map(product =>
                React.createElement(window.ProductCard, {
                    key: product.id,
                    product: product
                })
            )
        )
    );
};

window.SearchResults = SearchResults;
