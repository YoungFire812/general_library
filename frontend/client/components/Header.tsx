import { Link } from "react-router-dom";
import { ShoppingCart, Home, MessageSquare } from "lucide-react";

export default function Header({ onOpenUpload }: { onOpenUpload?: () => void }) {
  return (
    <header className="w-full bg-white shadow-sm">
      <div className="container mx-auto px-4 sm:px-8 lg:px-20">
        <div className="flex items-center justify-between py-4">
          {/* Logo/Home */}
          <Link
            to="/"
            className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-bold text-lg text-gray-900 hover:bg-gray-100 transition-colors"
          >
            <Home className="w-6 h-6" />
            <span className="hidden sm:inline">BookExchange</span>
          </Link>

          {/* Right Navigation */}
          <div className="flex items-center gap-2 sm:gap-4">
            {/* Cart Icon */}
            <Link
              to="/cart"
              className="flex items-center justify-center gap-2 px-3 sm:px-4 py-2 rounded-lg font-semibold text-sm text-gray-700 hover:bg-gray-100 transition-colors"
            >
              <ShoppingCart className="w-5 h-5" />
              <span className="hidden sm:inline">Cart</span>
            </Link>

            {/* Messages Icon */}
            <Link
              to="/messages"
              className="flex items-center justify-center gap-2 px-3 sm:px-4 py-2 rounded-lg font-semibold text-sm text-gray-700 hover:bg-gray-100 transition-colors"
            >
              <MessageSquare className="w-5 h-5" />
              <span className="hidden sm:inline">Messages</span>
            </Link>

            {/* Account Link */}
            <Link
              to="/account"
              className="flex items-center justify-center px-3 sm:px-5 py-2 sm:py-2.5 bg-[#FEF3F2] rounded-lg font-bold text-sm text-[#6750A4] hover:opacity-80 transition-opacity whitespace-nowrap"
            >
              Account
            </Link>

            {/* Upload Book Button */}
            <button
              onClick={() => onOpenUpload && onOpenUpload()}
              className="flex items-center justify-center px-3 sm:px-5 py-2 sm:py-2.5 bg-[#FEF3F2] rounded-lg font-bold text-sm text-[#B42318] hover:opacity-80 transition-opacity whitespace-nowrap"
            >
              Upload
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
