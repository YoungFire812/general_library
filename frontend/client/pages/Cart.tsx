import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ShoppingCart, ArrowLeft, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";

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
        // TODO: Replace with actual user_id
        const userId = "user-123"; // Placeholder
        const response = await fetch(`http://localhost:8000/${userId}/cart`);

        if (!response.ok) {
          throw new Error("Failed to fetch cart");
        }

        const data = await response.json();
        setCartItems(data.items || []);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load cart"
        );
        console.error("Error fetching cart:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchCart();
  }, []);

  const handleRemoveItem = async (itemId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/cart/${itemId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        setCartItems((prev) => prev.filter((item) => item.id !== itemId));
      } else {
        alert("Failed to remove item from cart");
      }
    } catch (error) {
      console.error("Error removing from cart:", error);
      alert("Error removing item");
    }
  };

  const handleCheckout = async () => {
    try {
      const response = await fetch("http://localhost:8000/checkout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          items: cartItems.map((item) => item.id),
        }),
      });

      if (response.ok) {
        alert("Order placed successfully!");
        setCartItems([]);
      } else {
        alert("Failed to place order");
      }
    } catch (error) {
      console.error("Error during checkout:", error);
      alert("Error during checkout");
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
              Shopping Cart
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
                Your cart is empty
              </h2>
              <p className="text-gray-600 mb-6">
                Start adding books to your cart to exchange!
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
                    Summary
                  </h2>

                  <div className="space-y-3 mb-6">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Books in cart</span>
                      <span className="font-semibold text-gray-900">
                        {cartItems.length}
                      </span>
                    </div>
                    <div className="border-t border-gray-200 pt-3">
                      <div className="flex justify-between">
                        <span className="font-semibold text-gray-900">Total</span>
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
                    Proceed to Checkout
                  </Button>

                  <p className="text-xs text-gray-500 text-center mt-4">
                    TODO: Add payment integration
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
