import { useState } from "react";
import { Star, MessageCircle, Trash2, Upload } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import ReviewSection from "@/components/ReviewSection";
import LeaveReviewForm from "@/components/LeaveReviewForm";

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
  const [profilePhoto, setProfilePhoto] = useState<string | null>(null);
  const [reviews, setReviews] = useState<Review[]>(mockReviews);
  const [averageRating] = useState(4.7);
  const [totalReviews] = useState(mockReviews.length);

  const handleDeleteBook = (bookId: string) => {
    setUserBooks((prev) => prev.filter((book) => book.id !== bookId));
  };

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfilePhoto(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAddReview = (name: string, text: string, rating: number) => {
    const newReview: Review = {
      author: name,
      text,
      rating,
    };
    setReviews([newReview, ...reviews]);
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
    <div className="min-h-screen bg-white">
      <main className="container mx-auto px-4 sm:px-8 py-12 sm:py-16">
        <div className="flex flex-col gap-8">
          {/* Profile Section */}
          <div className="flex flex-col sm:flex-row gap-6 sm:gap-8">
            {/* Avatar with Upload */}
            <div className="flex-shrink-0 relative">
              <div className="w-24 h-24 sm:w-32 sm:h-32 rounded-full bg-gradient-to-br from-purple-400 to-blue-500 flex items-center justify-center text-white text-3xl sm:text-4xl font-bold overflow-hidden">
                {profilePhoto ? (
                  <img
                    src={profilePhoto}
                    alt="Profile"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  "JD"
                )}
              </div>

              {/* Upload Photo Button */}
              <label className="absolute bottom-0 right-0 bg-[#6750A4] hover:bg-[#5a4494] text-white p-2 rounded-full cursor-pointer transition-colors shadow-lg">
                <Upload className="w-4 h-4" />
                <input
                  type="file"
                  accept="image/*"
                  onChange={handlePhotoUpload}
                  className="hidden"
                />
              </label>
            </div>

            {/* User Info */}
            <div className="flex-1">
              <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
                John Doe
              </h1>
              <p className="text-gray-600 mb-6">Member since January 2024</p>

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

          {/* Books Section */}
          <div className="pt-8 border-t border-gray-200">
            {/* Announcement Banner - Smaller */}
            <div className="mb-6 bg-gradient-to-r from-[#6750A4] to-[#5a4494] rounded-lg p-4 text-white">
              <h2 className="text-lg sm:text-xl font-bold mb-1">My Book Collection</h2>
              <p className="text-sm text-purple-100">
                {userBooks.length} book{userBooks.length !== 1 ? "s" : ""} available for exchange
              </p>
            </div>

            {userBooks.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600 text-sm">No books in your library yet</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 sm:gap-4">
                {userBooks.map((book) => (
                  <div
                    key={book.id}
                    className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-shadow border border-gray-200"
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
                    <div className="p-2">
                      <h3 className="font-semibold text-gray-900 line-clamp-2 text-xs mb-0.5">
                        {book.title}
                      </h3>
                      <p className="text-xs text-gray-600 line-clamp-1 mb-2">
                        {book.author}
                      </p>

                      {/* Delete Button */}
                      <button
                        onClick={() => handleDeleteBook(book.id)}
                        className="w-full flex items-center justify-center gap-1 bg-red-50 hover:bg-red-100 text-red-600 font-semibold py-1 rounded text-xs transition-colors"
                      >
                        <Trash2 className="w-3 h-3" />
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Reviews Section - Now Modular */}
          <ReviewSection reviews={reviews} />

          {/* Leave Review Form - Now Modular and Easily Removable */}
          <LeaveReviewForm onSubmit={handleAddReview} />
        </div>
      </main>
    </div>
  );
}
