import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
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
];

export default function ExchangeOfferModal({
  book,
  open,
  onClose,
}: ExchangeOfferModalProps) {
  const [selectedBook, setSelectedBook] = useState<string>("");
  const [message, setMessage] = useState<string>("");

  if (!book) return null;

  const handleSendOffer = () => {
    if (!selectedBook) {
      alert("Please select a book to offer");
      return;
    }

    // TODO: Replace with actual API call
    // const response = await fetch('/api/exchange-offers', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({
    //     offeredBookId: selectedBook,
    //     requestedBookId: book.id,
    //     message: message,
    //   }),
    // });

    console.log("Exchange offer submitted:", {
      offeredBookId: selectedBook,
      requestedBookId: book.id,
      message: message,
    });

    alert("Exchange offer sent successfully!");
    handleClose();
  };

  const handleClose = () => {
    setSelectedBook("");
    setMessage("");
    onClose();
  };

  const selectedUserBook = placeholderUserBooks.find(
    (b) => b.id === selectedBook
  );

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">
            Propose Book Exchange
          </DialogTitle>
        </DialogHeader>

        <div className="flex flex-col gap-6 py-4">
          {/* Exchange Overview */}
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between bg-gray-50 p-4 rounded-lg">
            {/* Requested Book */}
            <div className="flex-1 flex flex-col gap-2 text-center sm:text-left">
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
            <div className="text-2xl text-gray-400">⇄</div>

            {/* Offered Book */}
            <div className="flex-1 flex flex-col gap-2 text-center sm:text-left">
              <span className="text-xs text-gray-500 uppercase tracking-wide">
                You offer
              </span>
              {selectedUserBook ? (
                <div className="flex gap-3 items-start">
                  <img
                    src={selectedUserBook.coverImage}
                    alt={selectedUserBook.title}
                    className="w-12 h-16 object-cover rounded"
                  />
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 text-sm">
                      {selectedUserBook.title}
                    </h3>
                    <p className="text-xs text-gray-600">
                      {selectedUserBook.author}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-gray-400 italic">Select a book</div>
              )}
            </div>
          </div>

          {/* Select Your Book */}
          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-gray-900">
              Select Book from Your Library
            </label>
            <Select value={selectedBook} onValueChange={setSelectedBook}>
              <SelectTrigger className="h-12 border-gray-300">
                <SelectValue placeholder="Choose a book to offer..." />
              </SelectTrigger>
              <SelectContent>
                {placeholderUserBooks.map((b) => (
                  <SelectItem key={b.id} value={b.id}>
                    <div className="flex items-center gap-2">
                      <span>{b.title}</span>
                      <span className="text-xs text-gray-500">
                        by {b.author}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
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
              className="min-h-24 border-gray-300 resize-none"
            />
            <p className="text-xs text-gray-500">
              Share your thoughts about this exchange
            </p>
          </div>

          {/* Book Details Comparison */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="flex flex-col gap-3">
              <h4 className="font-semibold text-gray-900 text-sm">
                Requested Book
              </h4>
              <div className="text-sm text-gray-700 space-y-1">
                <p>
                  <span className="text-gray-500">Category:</span> {book.category}
                </p>
                <p>
                  <span className="text-gray-500">Author:</span> {book.author}
                </p>
                <p className="text-gray-600">{book.description}</p>
              </div>
            </div>

            {selectedUserBook && (
              <div className="flex flex-col gap-3">
                <h4 className="font-semibold text-gray-900 text-sm">
                  Your Book
                </h4>
                <div className="text-sm text-gray-700 space-y-1">
                  <p>
                    <span className="text-gray-500">Category:</span>{" "}
                    {selectedUserBook.category}
                  </p>
                  <p>
                    <span className="text-gray-500">Author:</span>{" "}
                    {selectedUserBook.author}
                  </p>
                  <p className="text-gray-600">{selectedUserBook.description}</p>
                </div>
              </div>
            )}
          </div>

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
