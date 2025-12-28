import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { X } from "lucide-react";
import { Book } from "./BooksList";

interface ExchangeOfferModalProps {
  book: Book | null;
  open: boolean;
  onClose: () => void;
}

// Placeholder books for the user's library - Replace with API data later
const placeholderUserBooks: Book[] = [
  {
    id: "user-1",
    title: "The Hobbit",
    author: "J.R.R. Tolkien",
    category: "Fantasy",
    description: "A fantasy adventure following Bilbo Baggins.",
    images: [
      "https://images.unsplash.com/photo-1507842217343-583f7270bfba?w=400&h=600&fit=crop",
    ],
    coverImage:
      "https://images.unsplash.com/photo-1507842217343-583f7270bfba?w=400&h=600&fit=crop",
  },
  {
    id: "user-2",
    title: "Dune",
    author: "Frank Herbert",
    category: "Science Fiction",
    description: "An epic science fiction novel set on the desert planet Arrakis.",
    images: [
      "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=600&fit=crop",
    ],
    coverImage:
      "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=600&fit=crop",
  },
  {
    id: "user-3",
    title: "Sherlock Holmes: A Study in Scarlet",
    author: "Arthur Conan Doyle",
    category: "Mystery",
    description: "The first Sherlock Holmes mystery novel.",
    images: [
      "https://images.unsplash.com/photo-1543002588-d4d8fca5f0b9?w=400&h=600&fit=crop",
    ],
    coverImage:
      "https://images.unsplash.com/photo-1543002588-d4d8fca5f0b9?w=400&h=600&fit=crop",
  },
  {
    id: "user-4",
    title: "The Lord of the Rings",
    author: "J.R.R. Tolkien",
    category: "Fantasy",
    description: "An epic fantasy trilogy about the quest to destroy the One Ring.",
    images: [
      "https://images.unsplash.com/photo-1507842217343-583f7270bfba?w=400&h=600&fit=crop",
    ],
    coverImage:
      "https://images.unsplash.com/photo-1507842217343-583f7270bfba?w=400&h=600&fit=crop",
  },
  {
    id: "user-5",
    title: "The Name of the Wind",
    author: "Patrick Rothfuss",
    category: "Fantasy",
    description: "A fantasy novel about a legendary figure telling his own story.",
    images: [
      "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=600&fit=crop",
    ],
    coverImage:
      "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=600&fit=crop",
  },
  {
    id: "user-6",
    title: "Foundation",
    author: "Isaac Asimov",
    category: "Science Fiction",
    description: "A science fiction epic spanning thousands of years.",
    images: [
      "https://images.unsplash.com/photo-1543002588-d4d8fca5f0b9?w=400&h=600&fit=crop",
    ],
    coverImage:
      "https://images.unsplash.com/photo-1543002588-d4d8fca5f0b9?w=400&h=600&fit=crop",
  },
];

export default function ExchangeOfferModal({
  book,
  open,
  onClose,
}: ExchangeOfferModalProps) {
  const [selectedBookIds, setSelectedBookIds] = useState<Set<string>>(new Set());
  const [message, setMessage] = useState<string>("");

  if (!book) return null;

  const toggleBookSelection = (bookId: string) => {
    setSelectedBookIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(bookId)) {
        newSet.delete(bookId);
      } else {
        newSet.add(bookId);
      }
      return newSet;
    });
  };

  const removeSelectedBook = (bookId: string) => {
    setSelectedBookIds((prev) => {
      const newSet = new Set(prev);
      newSet.delete(bookId);
      return newSet;
    });
  };

  const isBookSelected = (bookId: string) => {
    return selectedBookIds.has(bookId);
  };

  const getSelectedBooksDetails = () => {
    return Array.from(selectedBookIds).map((bookId) =>
      placeholderUserBooks.find((b) => b.id === bookId)
    );
  };

  const handleSendOffer = () => {
    if (selectedBookIds.size === 0) {
      alert("Please select at least one book to offer");
      return;
    }

    // TODO: Replace with actual API call
    // const response = await fetch('/api/exchange-offers', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({
    //     offeredBookIds: Array.from(selectedBookIds),
    //     requestedBookId: book.id,
    //     message: message,
    //   }),
    // });

    console.log("Exchange offer submitted:", {
      offeredBookIds: Array.from(selectedBookIds),
      requestedBookId: book.id,
      message: message,
    });

    alert("Exchange offer sent successfully!");
    handleClose();
  };

  const handleClose = () => {
    setSelectedBookIds(new Set());
    setMessage("");
    onClose();
  };

  const selectedBooksDetails = getSelectedBooksDetails();

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">
            Propose Book Exchange
          </DialogTitle>
        </DialogHeader>

        <div className="flex flex-col gap-6 py-4">
          {/* Exchange Overview */}
          <div className="flex flex-col sm:flex-row gap-4 items-start justify-between bg-gray-50 p-4 rounded-lg">
            {/* Requested Book */}
            <div className="flex-1 flex flex-col gap-2">
              <span className="text-xs text-gray-500 uppercase tracking-wide">
                You want
              </span>
              <div className="flex gap-3 items-start">
                <img
                  src={book.coverImage}
                  alt={book.title}
                  className="w-12 h-16 object-cover rounded"
                />
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 text-sm">
                    {book.title}
                  </h3>
                  <p className="text-xs text-gray-600">{book.author}</p>
                </div>
              </div>
            </div>

            {/* Exchange Arrow */}
            <div className="text-2xl text-gray-400 flex-shrink-0">⇄</div>

            {/* Offered Books Summary */}
            <div className="flex-1 flex flex-col gap-2">
              <span className="text-xs text-gray-500 uppercase tracking-wide">
                You offer ({selectedBookIds.size})
              </span>
              {selectedBooksDetails.length > 0 ? (
                <div className="flex gap-1.5 flex-wrap">
                  {selectedBooksDetails.map((sb) => (
                    <img
                      key={sb?.id}
                      src={sb?.coverImage}
                      alt={sb?.title}
                      title={sb?.title}
                      className="w-8 h-11 object-cover rounded border-2 border-[#6750A4]"
                    />
                  ))}
                </div>
              ) : (
                <div className="text-sm text-gray-400 italic">
                  Select books below
                </div>
              )}
            </div>
          </div>

          {/* Your Library Grid */}
          <div className="flex flex-col gap-3">
            <div>
              <label className="text-sm font-semibold text-gray-900">
                Select Books from Your Library
              </label>
              <p className="text-xs text-gray-500 mt-1">
                Click on books to select them for the exchange
              </p>
            </div>

            <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-6 gap-2 max-h-64 overflow-y-auto p-2 border border-gray-200 rounded-lg bg-white">
              {placeholderUserBooks.map((userBook) => {
                const isSelected = isBookSelected(userBook.id);

                return (
                  <button
                    key={userBook.id}
                    onClick={() => toggleBookSelection(userBook.id)}
                    className={`flex flex-col gap-1 p-1.5 rounded-lg border-2 transition-all ${
                      isSelected
                        ? "border-[#6750A4] bg-[#F3E5F5]"
                        : "border-gray-200 bg-white hover:border-[#6750A4]"
                    }`}
                    title={userBook.title}
                  >
                    {/* Book Cover */}
                    <div className="relative w-full">
                      <img
                        src={userBook.coverImage}
                        alt={userBook.title}
                        className="w-full aspect-[2/3] object-cover rounded"
                      />
                      {isSelected && (
                        <div className="absolute inset-0 bg-[#6750A4]/20 rounded flex items-center justify-center">
                          <div className="bg-[#6750A4] text-white rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold">
                            ✓
                          </div>
                        </div>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>

            <p className="text-xs text-gray-500">
              TODO: Replace with your actual books from API
            </p>
          </div>

          {/* Message Section */}
          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-gray-900">
              Message (Optional)
            </label>
            <Textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Add a message to the exchange offer..."
              className="min-h-20 border-gray-300 resize-none"
            />
            <p className="text-xs text-gray-500">
              Share your thoughts about this exchange
            </p>
          </div>

          {/* Selected Books Details */}
          {selectedBooksDetails.length > 0 && (
            <div className="flex flex-col gap-3 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-gray-900">Your Offer</h4>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {selectedBooksDetails.map((sb) => (
                  <div
                    key={sb?.id}
                    className="flex items-start justify-between p-3 bg-white rounded border border-gray-200"
                  >
                    <div className="flex gap-3 items-start flex-1">
                      <img
                        src={sb?.coverImage}
                        alt={sb?.title}
                        className="w-10 h-14 object-cover rounded flex-shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <h5 className="font-semibold text-sm text-gray-900 line-clamp-2">
                          {sb?.title}
                        </h5>
                        <p className="text-xs text-gray-600">{sb?.author}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {sb?.category}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeSelectedBook(sb?.id || "")}
                      className="p-1 hover:bg-red-50 rounded transition-colors flex-shrink-0"
                    >
                      <X className="w-4 h-4 text-red-600" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            <Button
              onClick={handleSendOffer}
              className="flex-1 bg-[#6750A4] hover:bg-[#5a4494] text-white font-semibold py-3 rounded-lg transition-colors"
            >
              Send Exchange Offer
            </Button>
            <Button
              onClick={handleClose}
              variant="outline"
              className="flex-1 border-2 border-gray-300 text-gray-900 font-semibold py-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Back
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
