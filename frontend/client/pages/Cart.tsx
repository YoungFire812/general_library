import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ShoppingCart, ArrowLeft, Trash2, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import Pagination from "@/components/Pagination";
import ExchangeOfferModal from "@/components/ExchangeOfferModal";

interface CartItem {
  id: string;
  title: string;
  author: string;
  category: string;
  coverImage: string;
  price?: number;
}

export default function Cart() {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCart = async () => {
      try {
        setLoading(true);
        const response = await fetch("/api/cart");

        if (response.ok) {
          const data = await response.json();
          setCartItems(data.items || []);
        } else {
          // Use mock data if API endpoint not available
          throw new Error("Cart endpoint not available");
        }
      } catch (err) {
        // Fallback to mock data for development
        console.log("Using mock cart data");
        const mockItems = [
          {
            id: "1",
            title: "The Great Gatsby",
            author: "F. Scott Fitzgerald",
            category: "Fiction",
            coverImage: "https://images.unsplash.com/photo-1507842217343-583f7270bfba?w=400&h=600&fit=crop",
          },
          {
            id: "2",
            title: "To Kill a Mockingbird",
            author: "Harper Lee",
            category: "Fiction",
            coverImage: "https://images.unsplash.com/photo-1543002588-d4d8fca5f0b9?w=400&h=600&fit=crop",
          },
        ];
        setCartItems(mockItems);
      } finally {
        setLoading(false);
      }
    };

    fetchCart();
  }, []);

  const handleRemoveItem = async (itemId: string) => {
    try {
      const response = await fetch(`/api/cart/${itemId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        setCartItems((prev) => prev.filter((item) => item.id !== itemId));
      } else {
        // Optimistically remove item from UI even if API fails
        setCartItems((prev) => prev.filter((item) => item.id !== itemId));
      }
    } catch (error) {
      console.error("Error removing from cart:", error);
      // Optimistically remove item from UI
      setCartItems((prev) => prev.filter((item) => item.id !== itemId));
    }
  };

  const handleCheckout = async () => {
    try {
      const response = await fetch("/api/checkout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          items: cartItems.map((item) => item.id),
        }),
      });

      if (response.ok) {
        alert("Ready to exchange! Visit Messages to start an exchange with a user.");
        // Don't clear items - keep them in basket for future exchanges
      } else {
        // For development, allow exchange even if API not implemented
        alert("Ready to exchange! Visit Messages to start an exchange with a user.");
      }
    } catch (error) {
      console.error("Error during exchange:", error);
      // For development, allow exchange even if API not implemented
      alert("Ready to exchange! Visit Messages to start an exchange with a user.");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white">
        <main className="container mx-auto px-4 sm:px-8 py-12 sm:py-16">
          <div className="flex items-center justify-center h-64">
            <p className="text-gray-600">Loading cart...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <main className="container mx-auto px-4 sm:px-8 py-12 sm:py-16">
        <div className="flex flex-col gap-8">
          {/* Header */}
          <div className="flex items-center gap-4">
            <Link
              to="/"
              className="flex items-center gap-2 text-[#6750A4] hover:opacity-70 transition-opacity"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="font-semibold">Back to Books</span>
            </Link>
            <div className="flex-1" />
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 flex items-center gap-3">
              <ShoppingCart className="w-8 h-8" />
              My Basket
            </h1>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {cartItems.length === 0 ? (
            <div className="text-center py-16">
              <ShoppingCart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Your basket is empty
              </h2>
              <p className="text-gray-600 mb-6">
                Start adding books to your basket to exchange!
              </p>
              <Link
                to="/"
                className="inline-block bg-[#6750A4] hover:bg-[#5a4494] text-white font-semibold px-6 py-3 rounded-lg transition-colors"
              >
                Browse Books
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Cart Items */}
              <div className="lg:col-span-2">
                <div className="bg-gray-50 rounded-lg p-4 sm:p-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    Items ({cartItems.length})
                  </h2>
                  <div className="space-y-3">
                    {cartItems.map((item) => (
                      <div
                        key={item.id}
                        className="bg-white rounded-lg p-4 flex gap-4 items-start"
                      >
                        {/* Book Image */}
                        <img
                          src={item.coverImage}
                          alt={item.title}
                          className="w-16 h-24 object-cover rounded flex-shrink-0"
                        />

                        {/* Book Details */}
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 text-sm sm:text-base">
                            {item.title}
                          </h3>
                          <p className="text-sm text-gray-600">{item.author}</p>
                          <span className="inline-block mt-2 text-xs font-medium text-[#6750A4] bg-[#F3E5F5] px-2 py-1 rounded">
                            {item.category}
                          </span>
                        </div>

                        {/* Remove Button */}
                        <button
                          onClick={() => handleRemoveItem(item.id)}
                          className="p-2 hover:bg-red-50 rounded transition-colors flex-shrink-0"
                          title="Remove from cart"
                        >
                          <Trash2 className="w-5 h-5 text-red-600" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Summary */}
              <div className="lg:col-span-1">
                <div className="bg-gray-50 rounded-lg p-6 sticky top-20">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    Basket Summary
                  </h2>

                  <div className="space-y-3 mb-6">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Books in basket</span>
                      <span className="font-semibold text-gray-900">
                        {cartItems.length}
                      </span>
                    </div>
                    <div className="border-t border-gray-200 pt-3">
                      <div className="flex justify-between">
                        <span className="font-semibold text-gray-900">Available</span>
                        <span className="font-bold text-lg text-[#6750A4]">
                          {cartItems.length} books
                        </span>
                      </div>
                    </div>
                  </div>

                  <Button
                    onClick={handleCheckout}
                    className="w-full bg-[#6750A4] hover:bg-[#5a4494] text-white font-semibold py-3 rounded-lg transition-colors"
                  >
                    Start Exchange
                  </Button>

                  <p className="text-xs text-gray-500 text-center mt-4">
                    Exchange one book at a time via Messages
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
