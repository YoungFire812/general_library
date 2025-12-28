import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, ShoppingCart } from "lucide-react";
import ExchangeOfferModal from "./ExchangeOfferModal";
import { Book } from "./BooksList";

interface BookDetailModalProps {
  book: Book | null;
  onClose: () => void;
}

export default function BookDetailModal({ book, onClose }: BookDetailModalProps) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [openExchange, setOpenExchange] = useState(false);

  if (!book) return null;

  const images = book.images || [book.coverImage];
  const currentImage = images[currentImageIndex];

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  const handleExchangeClick = () => {
    setOpenExchange(true);
  };

  const handleAddToCart = async () => {
    try {
      const response = await fetch("http://localhost:8000/cart", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          bookId: book.id,
        }),
      });

      if (response.ok) {
        alert("Book added to cart!");
      } else {
        alert("Failed to add book to cart");
      }
    } catch (error) {
      console.error("Error adding to cart:", error);
      alert("Error adding book to cart");
    }
  };

  return (
    <>
      <Dialog open={book !== null} onOpenChange={onClose}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto p-0 sm:p-6">
          <div className="flex flex-col gap-6 pt-6 sm:pt-0">
            {/* Image Carousel */}
            <div className="relative bg-gray-100 rounded-lg overflow-hidden">
              <div className="aspect-square sm:aspect-video relative">
                <img
                  src={currentImage}
                  alt={book.title}
                  className="w-full h-full object-cover"
                />

                {/* Navigation arrows */}
                {images.length > 1 && (
                  <>
                    <button
                      onClick={prevImage}
                      className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white p-2 rounded-full transition-colors z-10"
                    >
                      <ChevronLeft className="w-6 h-6" />
                    </button>
                    <button
                      onClick={nextImage}
                      className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white p-2 rounded-full transition-colors z-10"
                    >
                      <ChevronRight className="w-6 h-6" />
                    </button>
                  </>
                )}

                {/* Image indicator */}
                {images.length > 1 && (
                  <div className="absolute bottom-2 left-1/2 -translate-x-1/2 bg-black/50 text-white text-xs px-2 py-1 rounded">
                    {currentImageIndex + 1} / {images.length}
                  </div>
                )}
              </div>
            </div>

            {/* Book Information */}
            <div className="flex flex-col gap-4 px-4 sm:px-0">
              {/* Title and Author */}
              <div className="flex flex-col gap-2">
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">
                  {book.title}
                </h2>
                <p className="text-base sm:text-lg text-gray-600">{book.author}</p>
              </div>

              {/* Category and Details Grid */}
              <div className="grid grid-cols-2 gap-3 sm:gap-4">
                <div className="flex flex-col gap-1">
                  <span className="text-xs text-gray-500 uppercase tracking-wide">
                    Category
                  </span>
                  <span className="font-medium text-gray-900">{book.category}</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-xs text-gray-500 uppercase tracking-wide">
                    Book ID
                  </span>
                  <span className="font-medium text-gray-900 font-mono text-sm">
                    {book.id}
                  </span>
                </div>
              </div>

              {/* Description */}
              <div className="flex flex-col gap-2">
                <span className="text-xs text-gray-500 uppercase tracking-wide">
                  Description
                </span>
                <p className="text-sm sm:text-base text-gray-700 leading-relaxed">
                  {book.description}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 pt-4">
                <Button
                  onClick={() => setOpenExchange(true)}
                  className="flex-1 bg-[#6750A4] hover:bg-[#5a4494] text-white font-semibold py-3 rounded-lg transition-colors"
                >
                  Propose Exchange
                </Button>
                <Button
                  onClick={onClose}
                  variant="outline"
                  className="flex-1 border-2 border-gray-300 text-gray-900 font-semibold py-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Close
                </Button>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <ExchangeOfferModal
        book={book}
        open={openExchange}
        onClose={() => setOpenExchange(false)}
      />
    </>
  );
}
