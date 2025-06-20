import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class AIShoppingService:
    def __init__(self):
        # API Keys from environment variables
        self.phi3_api_key = os.getenv("PHI3_API_KEY", "")
        self.serpapi_key = os.getenv("SERPAPI_KEY", "")
        self.together_api_key = os.getenv("TOGETHER_API_KEY", "")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        
        # API Endpoints
        self.phi3_endpoint = "https://api.together.xyz/v1/chat/completions"
        self.serpapi_endpoint = "https://serpapi.com/search"
        self.together_endpoint = "https://api.together.xyz/v1/chat/completions"
        
        # User sessions to track filter conversations
        self.user_sessions = {}
        
        if not self.serpapi_key:
            logger.warning("SerpAPI key not found in environment variables")
        if not self.together_api_key and not self.openrouter_api_key:
            logger.warning("No AI service API keys found in environment variables")

    async def process_search_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language search query and return product recommendations
        """
        try:
            # Step 1: Parse query with Phi-3 Mini Instruct
            parsed_query = await self._parse_query_with_phi3(query)
            
            # Step 2: Search for products using SerpAPI
            search_results = await self._search_products_with_serpapi(parsed_query)
            
            # If no results from SerpAPI (rate limited), use fallback
            if not search_results:
                logger.warning("Using fallback due to SerpAPI rate limit")
                search_results = self._get_fallback_products(query)
            
            # Step 3: Analyze and score products with AI
            analyzed_products = await self._analyze_products_with_ai(search_results, query)
            
            # Step 4: Rank and format results
            ranked_products = self._rank_products(analyzed_products)
            
            return {
                "products": ranked_products[:10],  # Top 10 results
                "explanation": f"Found {len(ranked_products)} products matching your criteria: {query}",
                "search_id": str(uuid.uuid4())
            }
            
        except Exception as e:
            logger.error(f"Error processing search query: {str(e)}")
            # Provide fallback products even on error
            try:
                fallback_products = self._get_fallback_products(query)
                analyzed_products = await self._analyze_products_with_ai(fallback_products, query)
                ranked_products = self._rank_products(analyzed_products)
                
                return {
                    "products": ranked_products[:10],
                    "explanation": f"Showing sample results for: {query} (API temporarily unavailable)",
                    "search_id": str(uuid.uuid4())
                }
            except:
                return {
                    "products": [],
                    "explanation": f"Sorry, I encountered an error while searching: {str(e)}",
                    "search_id": str(uuid.uuid4())
                }

    async def process_chat_message(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Process a conversational message with interactive filter-based search
        """
        try:
            # Initialize session if new
            if session_id not in self.user_sessions:
                self.user_sessions[session_id] = {
                    "stage": "initial",
                    "product_keyword": None,
                    "current_filters": {},
                    "available_filters": [],
                    "current_filter_index": 0
                }
            
            session = self.user_sessions[session_id]
            
            # Extract product keyword if in initial stage
            if session["stage"] == "initial":
                keyword = await self._extract_product_keyword(message)
                if keyword:
                    session["product_keyword"] = keyword
                    session["stage"] = "getting_filters"
                    
                    # Get available filters for this product category
                    filters = await self._get_available_filters(keyword)
                    session["available_filters"] = filters
                    
                    if filters:
                        current_filter = filters[0]
                        return {
                            "message": f"Great! I found filters for {keyword}. Let's refine your search step by step.\n\n**{current_filter['name']}**: Please choose from these options:\n" + 
                                     "\n".join([f"• {opt}" for opt in current_filter['options']]),
                            "has_products": False,
                            "products": [],
                            "timestamp": datetime.now(),
                            "filter_options": current_filter['options'],
                            "filter_name": current_filter['name']
                        }
                    else:
                        # No filters available, proceed with basic search
                        results = await self._search_with_keyword(keyword)
                        return {
                            "message": f"Here are the search results for {keyword}:",
                            "has_products": True,
                            "products": results,
                            "timestamp": datetime.now()
                        }
                else:
                    return {
                        "message": "I'd like to help you find products! Please tell me what you're looking for (e.g., smartphone, speakers, earphones, laptop, etc.)",
                        "has_products": False,
                        "products": [],
                        "timestamp": datetime.now()
                    }
            
            # Handle filter selection
            elif session["stage"] == "getting_filters":
                filter_index = session["current_filter_index"]
                if filter_index < len(session["available_filters"]):
                    current_filter = session["available_filters"][filter_index]
                    
                    # Store the user's choice
                    session["current_filters"][current_filter["param"]] = message.strip()
                    session["current_filter_index"] += 1
                    
                    # Check if there are more filters
                    if session["current_filter_index"] < len(session["available_filters"]):
                        next_filter = session["available_filters"][session["current_filter_index"]]
                        return {
                            "message": f"**{next_filter['name']}**: Please choose from these options:\n" + 
                                     "\n".join([f"• {opt}" for opt in next_filter['options']]),
                            "has_products": False,
                            "products": [],
                            "timestamp": datetime.now(),
                            "filter_options": next_filter['options'],
                            "filter_name": next_filter['name']
                        }
                    else:
                        # All filters collected, perform search
                        session["stage"] = "searching"
                        results = await self._search_with_filters(session["product_keyword"], session["current_filters"])
                        
                        # Reset session for next search
                        self.user_sessions[session_id] = {
                            "stage": "initial",
                            "product_keyword": None,
                            "current_filters": {},
                            "available_filters": [],
                            "current_filter_index": 0
                        }
                        
                        return {
                            "message": f"Here are your filtered results for {session['product_keyword']}:",
                            "has_products": True,
                            "products": results,
                            "timestamp": datetime.now()
                        }
            
            # Default conversational response
            response_text = await self._generate_conversational_response(message)
            return {
                "message": response_text,
                "has_products": False,
                "products": [],
                "timestamp": datetime.now()
            }
                
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            return {
                "message": "I'm sorry, I encountered an error. Let's start fresh - what product are you looking for?",
                "has_products": False,
                "products": [],
                "timestamp": datetime.now()
            }

    async def _parse_query_with_phi3(self, query: str) -> Dict[str, Any]:
        """Parse natural language query using Phi-3 Mini Instruct"""
        if not self.phi3_api_key:
            # Fallback parsing without API
            return {
                "product_type": query,
                "price_range": None,
                "features": [],
                "brand_preference": None
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.phi3_api_key}",
                    "Content-Type": "application/json"
                }
                
                prompt = f"""
                Parse this shopping query and extract key information:
                Query: "{query}"
                
                Return JSON with: product_type, price_range, features, brand_preference
                """
                
                payload = {
                    "model": "microsoft/Phi-3-mini-4k-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200
                }
                
                async with session.post(self.phi3_endpoint, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        try:
                            return json.loads(content)
                        except json.JSONDecodeError:
                            logger.warning("Failed to parse Phi-3 response as JSON")
                            return {"product_type": query}
                    else:
                        logger.error(f"Phi-3 API error: {response.status}")
                        return {"product_type": query}
                        
        except Exception as e:
            logger.error(f"Error calling Phi-3 API: {str(e)}")
            return {"product_type": query}

    async def _search_products_with_serpapi(self, parsed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for products using SerpAPI Google Shopping"""
        if not self.serpapi_key:
            raise Exception("SerpAPI key not configured")
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "engine": "google_shopping",
                    "q": parsed_query.get("product_type", ""),
                    "api_key": self.serpapi_key,
                    "num": 10,  # Reduced to avoid rate limits
                    "gl": "in",  # India
                    "hl": "en"
                }
                
                async with session.get(self.serpapi_endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        shopping_results = data.get("shopping_results", [])
                        
                        products = []
                        for result in shopping_results:
                            product = {
                                "title": result.get("title", ""),
                                "price": result.get("price", ""),
                                "description": result.get("snippet", ""),
                                "image_url": result.get("thumbnail", ""),
                                "rating": result.get("rating"),
                                "reviews_count": result.get("reviews"),
                                "source": result.get("source", ""),
                                "url": result.get("link", ""),
                                "raw_data": result
                            }
                            products.append(product)
                        
                        return products
                    elif response.status == 429:
                        # Rate limit exceeded - return empty list to trigger fallback
                        logger.warning("SerpAPI rate limit exceeded")
                        return []
                    else:
                        error_text = await response.text()
                        logger.error(f"SerpAPI error {response.status}: {error_text}")
                        raise Exception(f"SerpAPI error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error calling SerpAPI: {str(e)}")
            raise

    async def _analyze_products_with_ai(self, products: List[Dict[str, Any]], original_query: str) -> List[Dict[str, Any]]:
        """Analyze products and calculate relevance scores using AI"""
        api_key = self.together_api_key or self.openrouter_api_key
        endpoint = self.together_endpoint if self.together_api_key else "https://openrouter.ai/api/v1/chat/completions"
        
        if not api_key:
            # Fallback scoring without AI
            logger.warning("No AI service API key available, using fallback scoring")
            for i, product in enumerate(products):
                product.update({
                    "relevance_score": max(0.1, 1.0 - (i * 0.1)),
                    "explanation": f"Product matches your search for: {original_query}"
                })
            return products
        
        analyzed_products = []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                for product in products:
                    prompt = f"""
                    Analyze this product for the query: "{original_query}"
                    
                    Product: {product['title']}
                    Price: {product['price']}
                    Description: {product['description']}
                    
                    Rate relevance (0-1) and explain why it matches or doesn't match.
                    Return JSON: {{"relevance_score": 0.8, "explanation": "reason"}}
                    """
                    
                    payload = {
                        "model": "meta-llama/Llama-2-70b-chat-hf" if self.together_api_key else "anthropic/claude-3-haiku",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 150
                    }
                    
                    try:
                        async with session.post(endpoint, headers=headers, json=payload) as response:
                            if response.status == 200:
                                data = await response.json()
                                content = data["choices"][0]["message"]["content"]
                                try:
                                    analysis = json.loads(content)
                                    product.update(analysis)
                                except json.JSONDecodeError:
                                    product.update({
                                        "relevance_score": 0.5,
                                        "explanation": "Unable to analyze product relevance"
                                    })
                            else:
                                product.update({
                                    "relevance_score": 0.5,
                                    "explanation": "Analysis unavailable"
                                })
                    except Exception as e:
                        logger.warning(f"Error analyzing product {product['title']}: {str(e)}")
                        product.update({
                            "relevance_score": 0.5,
                            "explanation": "Analysis unavailable"
                        })
                    
                    analyzed_products.append(product)
                
                return analyzed_products
                
        except Exception as e:
            logger.error(f"Error in AI product analysis: {str(e)}")
            # Return products with default scores
            for i, product in enumerate(products):
                product.update({
                    "relevance_score": max(0.1, 1.0 - (i * 0.1)),
                    "explanation": f"Product matches your search criteria"
                })
            return products

    def _rank_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank products by relevance score and format for response"""
        # Sort by relevance score
        sorted_products = sorted(products, key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Format products for API response
        formatted_products = []
        for i, product in enumerate(sorted_products):
            formatted_product = {
                "id": str(uuid.uuid4()),
                "title": product.get("title", "Unknown Product"),
                "description": product.get("description", ""),
                "price": product.get("price", "Price not available"),
                "currency": "₹",
                "image_url": product.get("image_url", "/static/placeholder-product.svg"),
                "rating": product.get("rating"),
                "reviews_count": product.get("reviews_count"),
                "availability": "In Stock",
                "source": product.get("source", "Unknown"),
                "url": product.get("url", "#"),
                "relevance_score": product.get("relevance_score", 0.5),
                "explanation": product.get("explanation", "Recommended based on your search criteria")
            }
            formatted_products.append(formatted_product)
        
        return formatted_products

    async def _analyze_message_intent(self, message: str) -> Dict[str, Any]:
        """Analyze if a message requires product search or is conversational"""
        # Simple keyword-based intent detection
        search_keywords = [
            "buy", "purchase", "find", "looking for", "need", "want", "search",
            "recommend", "suggest", "best", "cheap", "expensive", "under", "above",
            "smartphone", "laptop", "watch", "headphones", "shoes", "clothes"
        ]
        
        message_lower = message.lower()
        requires_search = any(keyword in message_lower for keyword in search_keywords)
        
        return {
            "requires_search": requires_search,
            "intent": "product_search" if requires_search else "conversation"
        }

    def _get_fallback_products(self, query: str) -> List[Dict[str, Any]]:
        """Generate fallback product data when SerpAPI is unavailable"""
        query_lower = query.lower()
        
        # Smartphone fallbacks
        if any(word in query_lower for word in ["smartphone", "phone", "mobile"]):
            return [
                {
                    "title": "Samsung Galaxy A54 5G (Awesome Blue, 128GB)",
                    "price": "₹38,999",
                    "description": "6.4-inch Super AMOLED display, 50MP triple camera, 5000mAh battery",
                    "image_url": "https://images.samsung.com/is/image/samsung/p6pim/in/2202/gallery/in-galaxy-a54-5g-a546-sm-a546elvcins-534851043",
                    "rating": 4.3,
                    "reviews_count": 15420,
                    "source": "Amazon",
                    "url": "https://amazon.in",
                },
                {
                    "title": "Realme 11 Pro+ 5G (Oasis Green, 256GB)",
                    "price": "₹31,999",
                    "description": "6.7-inch curved AMOLED, 200MP camera, 100W SuperVOOC charging",
                    "image_url": "https://image01.realme.net/general/20230510/1683709141064.jpg",
                    "rating": 4.2,
                    "reviews_count": 8934,
                    "source": "Flipkart",
                    "url": "https://flipkart.com",
                }
            ]
        
        # Laptop fallbacks
        elif any(word in query_lower for word in ["laptop", "computer"]):
            return [
                {
                    "title": "HP Pavilion 15 Intel Core i5 12th Gen Laptop",
                    "price": "₹56,999",
                    "description": "15.6-inch FHD, 8GB RAM, 512GB SSD, Windows 11",
                    "image_url": "https://ssl-product-images.www8-hp.com/digmedialib/prodimg/lowres/c08140467.png",
                    "rating": 4.1,
                    "reviews_count": 2341,
                    "source": "HP Store",
                    "url": "https://hp.com",
                }
            ]
        
        # Default fallback for any query
        else:
            return [
                {
                    "title": f"Sample Product for {query}",
                    "price": "₹15,999",
                    "description": "High-quality product matching your search criteria",
                    "image_url": "https://via.placeholder.com/300x200?text=Product",
                    "rating": 4.0,
                    "reviews_count": 500,
                    "source": "Sample Store",
                    "url": "#",
                }
            ]

    async def _extract_product_keyword(self, message: str) -> Optional[str]:
        """Extract product keyword from user message"""
        # Common product categories
        product_keywords = [
            "smartphone", "phone", "mobile", "iphone", "android",
            "laptop", "computer", "macbook", "chromebook",
            "speakers", "speaker", "bluetooth speaker",
            "earphones", "headphones", "earbuds", "airpods",
            "tablet", "ipad",
            "watch", "smartwatch", "fitness tracker",
            "camera", "dslr", "mirrorless",
            "tv", "television", "smart tv",
            "mouse", "keyboard", "webcam",
            "charger", "power bank", "cable",
            "case", "cover", "screen protector"
        ]
        
        message_lower = message.lower()
        for keyword in product_keywords:
            if keyword in message_lower:
                return keyword
        
        return None

    async def _get_available_filters(self, keyword: str) -> List[Dict[str, Any]]:
        """Get available Google Shopping filters for a product category"""
        
        # Define filters based on product categories
        if keyword in ["smartphone", "phone", "mobile", "iphone", "android"]:
            return [
                {
                    "name": "Brand",
                    "param": "brand",
                    "options": ["Samsung", "Apple", "OnePlus", "Xiaomi", "Realme", "Oppo", "Vivo", "Google", "Nothing"]
                },
                {
                    "name": "Price Range",
                    "param": "price",
                    "options": ["Under ₹10,000", "₹10,000 - ₹20,000", "₹20,000 - ₹40,000", "₹40,000 - ₹60,000", "Above ₹60,000"]
                },
                {
                    "name": "Storage",
                    "param": "storage",
                    "options": ["64GB", "128GB", "256GB", "512GB", "1TB"]
                },
                {
                    "name": "RAM",
                    "param": "ram",
                    "options": ["4GB", "6GB", "8GB", "12GB", "16GB"]
                }
            ]
        
        elif keyword in ["laptop", "computer", "macbook", "chromebook"]:
            return [
                {
                    "name": "Brand",
                    "param": "brand",
                    "options": ["HP", "Dell", "Lenovo", "Asus", "Acer", "Apple", "MSI", "Samsung"]
                },
                {
                    "name": "Price Range",
                    "param": "price",
                    "options": ["Under ₹30,000", "₹30,000 - ₹50,000", "₹50,000 - ₹80,000", "₹80,000 - ₹1,20,000", "Above ₹1,20,000"]
                },
                {
                    "name": "Processor",
                    "param": "processor",
                    "options": ["Intel Core i3", "Intel Core i5", "Intel Core i7", "Intel Core i9", "AMD Ryzen 5", "AMD Ryzen 7", "Apple M1/M2"]
                },
                {
                    "name": "RAM",
                    "param": "ram",
                    "options": ["4GB", "8GB", "16GB", "32GB"]
                }
            ]
            
        elif keyword in ["speakers", "speaker", "bluetooth speaker"]:
            return [
                {
                    "name": "Brand",
                    "param": "brand",
                    "options": ["JBL", "Sony", "Bose", "Marshall", "Ultimate Ears", "Boat", "Portronics"]
                },
                {
                    "name": "Price Range",
                    "param": "price",
                    "options": ["Under ₹2,000", "₹2,000 - ₹5,000", "₹5,000 - ₹10,000", "₹10,000 - ₹20,000", "Above ₹20,000"]
                },
                {
                    "name": "Connectivity",
                    "param": "connectivity",
                    "options": ["Bluetooth", "Wi-Fi", "Wired", "Multi-room"]
                }
            ]
            
        elif keyword in ["earphones", "headphones", "earbuds", "airpods"]:
            return [
                {
                    "name": "Brand",
                    "param": "brand",
                    "options": ["Apple", "Sony", "Bose", "JBL", "Sennheiser", "Boat", "OnePlus", "Samsung"]
                },
                {
                    "name": "Price Range",
                    "param": "price",
                    "options": ["Under ₹1,500", "₹1,500 - ₹5,000", "₹5,000 - ₹10,000", "₹10,000 - ₹20,000", "Above ₹20,000"]
                },
                {
                    "name": "Type",
                    "param": "type",
                    "options": ["True Wireless", "Wireless", "Wired", "Over-ear", "On-ear", "In-ear"]
                },
                {
                    "name": "Features",
                    "param": "features",
                    "options": ["Active Noise Cancellation", "Wireless Charging", "Water Resistant", "Gaming", "Sports"]
                }
            ]
        
        # Default filters for other products
        return [
            {
                "name": "Price Range",
                "param": "price",
                "options": ["Under ₹1,000", "₹1,000 - ₹5,000", "₹5,000 - ₹10,000", "₹10,000 - ₹25,000", "Above ₹25,000"]
            },
            {
                "name": "Brand",
                "param": "brand",
                "options": ["Popular Brands", "Premium Brands", "Budget Brands"]
            }
        ]

    async def _search_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Search Google Shopping with just the keyword"""
        return await self._search_products_with_serpapi({"product_type": keyword})

    async def _search_with_filters(self, keyword: str, filters: Dict[str, str]) -> List[Dict[str, Any]]:
        """Search Google Shopping with keyword and applied filters"""
        
        # Build search query with filters
        search_query = keyword
        
        # Add filters to search query
        if "brand" in filters and filters["brand"] not in ["Popular Brands", "Premium Brands", "Budget Brands"]:
            search_query += f" {filters['brand']}"
        
        if "price" in filters:
            price_filter = filters["price"]
            if "Under" in price_filter:
                price_value = price_filter.split("₹")[1].replace(",", "")
                search_query += f" under {price_value}"
            elif "-" in price_filter:
                search_query += f" {price_filter.replace('₹', 'Rs ')}"
        
        if "storage" in filters:
            search_query += f" {filters['storage']}"
            
        if "ram" in filters:
            search_query += f" {filters['ram']} RAM"
            
        if "processor" in filters:
            search_query += f" {filters['processor']}"
            
        if "type" in filters:
            search_query += f" {filters['type']}"
            
        if "features" in filters:
            search_query += f" {filters['features']}"
            
        if "connectivity" in filters:
            search_query += f" {filters['connectivity']}"

        logger.info(f"Searching with filtered query: {search_query}")
        
        # Use existing search method with enhanced query
        try:
            if not self.serpapi_key:
                # Return filtered fallback products
                return self._get_filtered_fallback_products(keyword, filters)
                
            async with aiohttp.ClientSession() as session:
                params = {
                    "engine": "google_shopping",
                    "q": search_query,
                    "api_key": self.serpapi_key,
                    "num": 10,
                    "gl": "in",
                    "hl": "en"
                }
                
                # Add price filter if available
                if "price" in filters:
                    price_filter = filters["price"]
                    if "Under ₹" in price_filter:
                        max_price = price_filter.split("₹")[1].replace(",", "")
                        params["max_price"] = max_price
                    elif "-" in price_filter and "₹" in price_filter:
                        prices = price_filter.replace("₹", "").replace(",", "").split(" - ")
                        if len(prices) == 2:
                            params["min_price"] = prices[0].strip()
                            params["max_price"] = prices[1].strip()
                
                async with session.get(self.serpapi_endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        shopping_results = data.get("shopping_results", [])
                        
                        products = []
                        for result in shopping_results:
                            product = {
                                "title": result.get("title", ""),
                                "price": result.get("price", ""),
                                "description": result.get("snippet", ""),
                                "image_url": result.get("thumbnail", ""),
                                "rating": result.get("rating"),
                                "reviews_count": result.get("reviews"),
                                "source": result.get("source", ""),
                                "url": result.get("link", ""),
                                "raw_data": result
                            }
                            products.append(product)
                        
                        return products
                    elif response.status == 429:
                        logger.warning("SerpAPI rate limit exceeded, using filtered fallback")
                        return self._get_filtered_fallback_products(keyword, filters)
                    else:
                        logger.error(f"SerpAPI error {response.status}")
                        return self._get_filtered_fallback_products(keyword, filters)
                        
        except Exception as e:
            logger.error(f"Error in filtered search: {str(e)}")
            return self._get_filtered_fallback_products(keyword, filters)

    def _get_filtered_fallback_products(self, keyword: str, filters: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate filtered fallback products based on user selections"""
        base_products = self._get_fallback_products(keyword)
        
        # Apply basic filtering logic to fallback products
        filtered_products = []
        for product in base_products:
            # Check if product matches selected brand
            if "brand" in filters:
                brand = filters["brand"]
                if brand not in ["Popular Brands", "Premium Brands", "Budget Brands"]:
                    if brand.lower() not in product["title"].lower():
                        continue
            
            # Check price range
            if "price" in filters:
                price_filter = filters["price"]
                product_price = product.get("price", "₹0").replace("₹", "").replace(",", "")
                try:
                    price_num = int(product_price)
                    if "Under ₹" in price_filter:
                        max_price = int(price_filter.split("₹")[1].replace(",", ""))
                        if price_num >= max_price:
                            continue
                    elif "-" in price_filter:
                        prices = price_filter.replace("₹", "").replace(",", "").split(" - ")
                        if len(prices) == 2:
                            min_price, max_price = int(prices[0].strip()), int(prices[1].strip())
                            if not (min_price <= price_num <= max_price):
                                continue
                except:
                    pass
            
            # Add filter information to explanation
            filter_info = []
            for key, value in filters.items():
                filter_info.append(f"{key.title()}: {value}")
            
            product["explanation"] = f"Matches your filters - {', '.join(filter_info)}"
            filtered_products.append(product)
        
        return filtered_products if filtered_products else base_products

    async def _generate_conversational_response(self, message: str) -> str:
        """Generate a conversational response for non-search queries"""
        # Simple conversational responses
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        thanks = ["thank you", "thanks", "appreciate"]
        help_requests = ["help", "how", "what can you do"]
        
        message_lower = message.lower()
        
        if any(greeting in message_lower for greeting in greetings):
            return "Hello! I'm your AI Shopping Agent. I can help you find products based on your needs. Just tell me what you're looking for!"
        
        elif any(thank in message_lower for thank in thanks):
            return "You're welcome! Is there anything else I can help you find today?"
        
        elif any(help_word in message_lower for help_word in help_requests):
            return "I can help you find products by understanding your natural language queries. For example, you can say 'I need a smartphone under ₹20000 with good camera' and I'll find the best options for you!"
        
        else:
            return "I'm here to help you find products! Could you tell me what you're looking for? I can search for electronics, clothing, accessories, and much more."
