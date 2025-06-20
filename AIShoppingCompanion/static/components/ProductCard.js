const ProductCard = ({ product }) => {
    const renderStars = (rating) => {
        if (!rating) return null;
        
        const stars = [];
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 !== 0;
        
        for (let i = 0; i < 5; i++) {
            if (i < fullStars) {
                stars.push(React.createElement('i', { key: i, className: 'fas fa-star star' }));
            } else if (i === fullStars && hasHalfStar) {
                stars.push(React.createElement('i', { key: i, className: 'fas fa-star-half-alt star' }));
            } else {
                stars.push(React.createElement('i', { key: i, className: 'far fa-star star empty' }));
            }
        }
        
        return stars;
    };

    const handleViewProduct = () => {
        if (product.url && product.url !== '#') {
            window.open(product.url, '_blank', 'noopener,noreferrer');
        }
    };

    const formatPrice = (price) => {
        if (!price || price === 'Price not available') {
            return 'Price not available';
        }
        return price.toString().includes('₹') ? price : `₹${price}`;
    };

    const getScoreColor = (score) => {
        if (score >= 0.8) return '#28A745';
        if (score >= 0.6) return '#FFC107';
        return '#FF6B35';
    };

    return React.createElement('div', { className: 'product-card' },
        // Relevance Score Badge
        React.createElement('div', { 
            className: 'relevance-score',
            style: { backgroundColor: getScoreColor(product.relevance_score) }
        }, `${Math.round(product.relevance_score * 100)}% Match`),
        
        // Product Image
        React.createElement('img', {
            src: product.image_url || 'https://pixabay.com/get/gf2b746582ab10cd2ed3059513d95d5d15fbec46e7bf60968e1a761578bff9eb1db11f4031c82617cac036f5aef3f0bff6e2be29122bf6e914545390fb0c9384c_1280.jpg',
            alt: product.title,
            className: 'product-image',
            onError: (e) => {
                e.target.src = 'https://pixabay.com/get/gf2b746582ab10cd2ed3059513d95d5d15fbec46e7bf60968e1a761578bff9eb1db11f4031c82617cac036f5aef3f0bff6e2be29122bf6e914545390fb0c9384c_1280.jpg';
            }
        }),
        
        // Product Content
        React.createElement('div', { className: 'product-content' },
            React.createElement('h3', { className: 'product-title' }, product.title),
            React.createElement('div', { className: 'product-price' }, formatPrice(product.price)),
            
            // Rating
            product.rating && React.createElement('div', { className: 'product-rating' },
                React.createElement('div', { className: 'stars' }, ...renderStars(product.rating)),
                React.createElement('span', { className: 'rating-text' },
                    `${product.rating} ${product.reviews_count ? `(${product.reviews_count} reviews)` : ''}`
                )
            ),
            
            // Description
            product.description && React.createElement('p', { className: 'product-description' }, product.description),
            
            // AI Explanation
            React.createElement('div', { className: 'explanation' },
                React.createElement('strong', null, 'Why recommended: '),
                product.explanation
            ),
            
            // Product Footer
            React.createElement('div', { className: 'product-footer' },
                React.createElement('span', { className: 'product-source' }, 
                    React.createElement('i', { className: 'fas fa-store' }),
                    ` ${product.source}`
                ),
                React.createElement('button', {
                    className: 'view-product-button',
                    onClick: handleViewProduct,
                    disabled: !product.url || product.url === '#'
                }, 'View Product')
            )
        )
    );
};

window.ProductCard = ProductCard;
