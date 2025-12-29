import { useState } from "react";
import { Star } from "lucide-react";
import { Button } from "@/components/ui/button";

interface LeaveReviewFormProps {
  onSubmit: (name: string, text: string, rating: number) => void;
}

export default function LeaveReviewForm({ onSubmit }: LeaveReviewFormProps) {
  const [name, setName] = useState("");
  const [reviewText, setReviewText] = useState("");
  const [rating, setRating] = useState(5);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim() && reviewText.trim()) {
      onSubmit(name, reviewText, rating);
      setName("");
      setReviewText("");
      setRating(5);
      setSubmitted(true);
      setTimeout(() => setSubmitted(false), 3000);
    }
  };

  return (
    <div className="pt-8 border-t border-gray-200">
      <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-6">
        Leave a Review
      </h2>

      <form onSubmit={handleSubmit} className="bg-gradient-to-r from-gray-50 to-white rounded-lg p-6 border border-gray-200">
        {/* Name Input */}
        <div className="mb-4">
          <label htmlFor="name" className="block text-sm font-semibold text-gray-900 mb-2">
            Your Name
          </label>
          <input
            id="name"
            type="text"
            placeholder="e.g., Jane D."
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6750A4]"
          />
        </div>

        {/* Review Text */}
        <div className="mb-4">
          <label htmlFor="review" className="block text-sm font-semibold text-gray-900 mb-2">
            Your Review
          </label>
          <textarea
            id="review"
            placeholder="Share your experience..."
            value={reviewText}
            onChange={(e) => setReviewText(e.target.value)}
            rows={4}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6750A4] resize-none"
          />
        </div>

        {/* Rating */}
        <div className="mb-6">
          <label className="block text-sm font-semibold text-gray-900 mb-2">
            Rating
          </label>
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setRating(star)}
                className="focus:outline-none transition-transform hover:scale-110"
              >
                <Star
                  className={`w-6 h-6 ${
                    star <= rating
                      ? "fill-yellow-400 text-yellow-400"
                      : "text-gray-300"
                  }`}
                />
              </button>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          className="w-full bg-[#6750A4] hover:bg-[#5a4494] text-white font-semibold py-2 rounded-lg transition-colors"
        >
          Submit Review
        </Button>

        {submitted && (
          <p className="text-sm text-green-600 font-semibold mt-3">
            ✓ Thank you for your review!
          </p>
        )}
      </form>
    </div>
  );
}
