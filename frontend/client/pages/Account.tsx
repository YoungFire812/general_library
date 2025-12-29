import { useState } from "react";
import { Star, MessageCircle, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

interface UserBook {
  id: string;
  title: string;
  author: string;
  coverImage: string;
  dateAdded: string;
}

interface Review {
  author: string;
  text: string;
  rating: number;
}

const mockUserBooks: UserBook[] = [
  {
    id: "1",
    title: "The Great Gatsby",
    author: "F. Scott Fitzgerald",
    coverImage: "https://images.unsplash.com/photo-1507842217343-583f7270bfba?w=400&h=600&fit=crop",
    dateAdded: "2024-01-15",
  },
  {
    id: "2",
    title: "To Kill a Mockingbird",
    author: "Harper Lee",
    coverImage: "https://images.unsplash.com/photo-1543002588-d4d8fca5f0b9?w=400&h=600&fit=crop",
    dateAdded: "2024-01-20",
  },
  {
    id: "3",
    title: "1984",
    author: "George Orwell",
    coverImage: "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=600&fit=crop",
    dateAdded: "2024-02-05",
  },
];

const mockReviews: Review[] = [
  {
    author: "Sarah M.",
    text: "Great books and very responsive communicator. Highly recommend!",
    rating: 5,
  },
  {
    author: "John D.",
    text: "Books were in excellent condition. Quick delivery.",
    rating: 5,
  },
  {
    author: "Emma T.",
    text: "Good selection of books. Pleasant to work with.",
    rating: 4,
  },
];

export default function Account() {
  const [userBooks, setUserBooks] = useState<UserBook[]>(mockUserBooks);
  const [averageRating] = useState(4.7);
  const [totalReviews] = useState(mockReviews.length);

  const handleDeleteBook = (bookId: string) => {
    setUserBooks((prev) => prev.filter((book) => book.id !== bookId));
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= rating ? "fill-yellow-400 text-yellow-400" : "text-gray-300"
            }`}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="container mx-auto px-4 sm:px-8 py-12 sm:py-16">
        <div className="flex flex-col gap-8">
          {/* Profile Section */}
          <div className="bg-white rounded-lg shadow-md p-6 sm:p-8">
            <div className="flex flex-col sm:flex-row gap-6 sm:gap-8">
              {/* Avatar */}
              <div className="flex-shrink-0">
                <div className="w-24 h-24 sm:w-32 sm:h-32 rounded-full bg-gradient-to-br from-purple-400 to-blue-500 flex items-center justify-center text-white text-3xl sm:text-4xl font-bold">
                  JD
                </div>
              </div>

              {/* User Info */}
              <div className="flex-1">
                <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
                  John Doe
                </h1>
                <p className="text-gray-600 mb-4">Member since January 2024</p>

                {/* Rating Section */}
                <div className="mb-6">
                  <div className="flex items-center gap-4 mb-2">
                    <div className="flex items-center gap-2">
                      {renderStars(Math.round(averageRating))}
                      <span className="text-lg font-semibold text-gray-900">
                        {averageRating}
                      </span>
                    </div>
                    <span className="text-sm text-gray-600">
                      ({totalReviews} reviews)
                    </span>
                  </div>
                </div>

                {/* Message Button */}
                <Link
                  to="/messages"
                  className="inline-flex items-center gap-2 bg-[#6750A4] hover:bg-[#5a4494] text-white font-semibold px-6 py-3 rounded-lg transition-colors"
                >
                  <MessageCircle className="w-5 h-5" />
                  Send Message
                </Link>
              </div>
            </div>
          </div>

          {/* Reviews Section */}
          <div className="bg-white rounded-lg shadow-md p-6 sm:p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Reviews</h2>
            <div className="space-y-6">
              {mockReviews.map((review, index) => (
                <div
                  key={index}
                  className="pb-6 border-b border-gray-200 last:pb-0 last:border-b-0"
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-semibold text-gray-900">{review.author}</h3>
                    {renderStars(review.rating)}
                  </div>
                  <p className="text-gray-600">{review.text}</p>
                </div>
              ))}
            </div>
          </div>

          {/* My Books Section */}
          <div className="bg-white rounded-lg shadow-md p-6 sm:p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              My Library ({userBooks.length} books)
            </h2>

            {userBooks.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-600 mb-4">No books in your library yet</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {userBooks.map((book) => (
                  <div
                    key={book.id}
                    className="bg-gray-50 rounded-lg overflow-hidden hover:shadow-md transition-shadow"
                  >
                    {/* Book Image */}
                    <div className="aspect-[3/4] overflow-hidden bg-gray-200">
                      <img
                        src={book.coverImage}
                        alt={book.title}
                        className="w-full h-full object-contain"
                      />
                    </div>

                    {/* Book Info */}
                    <div className="p-4">
                      <h3 className="font-semibold text-gray-900 line-clamp-2 mb-1">
                        {book.title}
                      </h3>
                      <p className="text-sm text-gray-600 mb-3">{book.author}</p>
                      <p className="text-xs text-gray-500 mb-4">
                        Added {new Date(book.dateAdded).toLocaleDateString()}
                      </p>

                      {/* Delete Button */}
                      <button
                        onClick={() => handleDeleteBook(book.id)}
                        className="w-full flex items-center justify-center gap-2 bg-red-50 hover:bg-red-100 text-red-600 font-semibold py-2 rounded transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
