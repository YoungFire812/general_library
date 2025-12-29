import { Star } from "lucide-react";

interface Review {
  author: string;
  text: string;
  rating: number;
}

interface ReviewSectionProps {
  reviews: Review[];
}

function renderStars(rating: number) {
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
}

export default function ReviewSection({ reviews }: ReviewSectionProps) {
  return (
    <div className="pt-8 border-t border-gray-200">
      <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-8">
        Community Reviews
      </h2>

      {reviews.length === 0 ? (
        <p className="text-gray-600">No reviews yet</p>
      ) : (
        <div className="space-y-6">
          {reviews.map((review, index) => (
            <div
              key={index}
              className="bg-gradient-to-r from-gray-50 to-white rounded-lg p-6 border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-semibold text-gray-900 text-lg">
                  {review.author}
                </h3>
                {renderStars(review.rating)}
              </div>
              <p className="text-gray-700 leading-relaxed">{review.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
