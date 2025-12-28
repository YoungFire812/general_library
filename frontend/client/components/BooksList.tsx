import { useState } from "react";
import { ShoppingCart } from "lucide-react";
import BookDetailModal from "./BookDetailModal";

export interface Book {
  id: string;
  title: string;
  author: string;
  category: string;
  description: string;
  images: string[];
  coverImage: string;
}

// Placeholder data - Replace with API data later
const placeholderBooks: Book[] = [
  {
    id: "1",
    title: "The Great Gatsby",
    author: "F. Scott Fitzgerald",
    category: "Fiction",
    description:
      "A classic American novel set in the Jazz Age, exploring themes of wealth, love, and the American Dream.",
    images: [
      "https://images.unsplash.com/photo-1507842217343-583f7270bfba?w=400&h=600&fit=crop",
      "https://images.unsplash.com/photo-1495446815901-a7297e3ffe02?w=400&h=600&fit=crop",
    ],
    coverImage:
      "https://images.unsplash.com/photo-1507842217343-583f7270bfba?w=400&h=600&fit=crop",
  },
  {
    id: "2",
    title: "To Kill a Mockingbird",
    author: "Harper Lee",
    category: "Fiction",
    description:
      "A gripping tale of racial injustice and childhood innocence in the American South.",
    images: [
      "https://images.unsplash.com/photo-1543002588-d4d8fca5f0b9?w=400&h=600&fit=crop",
      "https://images.unsplash.com/photo-1507842217343-583f7270bfba?w=400&h=600&fit=crop",
    ],
    coverImage:
      "https://images.unsplash.com/photo-1543002588-d4d8fca5f0b9?w=400&h=600&fit=crop",
  },
  {
    id: "3",
    title: "1984",
    author: "George Orwell",
    category: "Science Fiction",
    description:
      "A dystopian novel depicting a totalitarian society and themes of surveillance and control.",
    images: [
      "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=600&fit=crop",
      "https://images.unsplash.com/photo-1507842217343-583f7270bfba?w=400&h=600&fit=crop",
    ],
    coverImage:
      "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=600&fit=crop",
  },
  {
    id: "4",
    title: "Pride and Prejudice",
    author: "Jane Austen",
    category: "Romance",
    description:
      "A timeless romance novel exploring love, social class, and personal growth in Regency England.",
    images: [
      "https://images.unsplash.com/photo-1548122328-c9526d6d1f6d?w=400&h=600&fit=crop",
      "https://images.unsplash.com/photo-1507842217343-583f7270bfba?w=400&h=600&fit=crop",
    ],
    coverImage:
      "https://images.unsplash.com/photo-1548122328-c9526d6d1f6d?w=400&h=600&fit=crop",
  },
  {
    id: "5",
    title: "The Catcher in the Rye",
    author: "J.D. Salinger",
    category: "Fiction",
    description:
      "A controversial novel following the teenage protagonist Holden Caulfield as he navigates adolescence.",
    images: [
      "https://images.unsplash.com/photo-1507842217343-583f7270bfba?w=400&h=600&fit=crop",
      "https://images.unsplash.com/photo-1543002588-d4d8fca5f0b9?w=400&h=600&fit=crop",
    ],
    coverImage:
      "https://images.unsplash.com/photo-1507842217343-583f7270bfba?w=400&h=600&fit=crop",
  },
  {
    id: "6",
    title: "Brave New World",
    author: "Aldous Huxley",
    category: "Science Fiction",
    description:
      "A futuristic novel depicting a seemingly perfect world controlled through conditioning and drugs.",
    images: [
      "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=600&fit=crop",
      "https://images.unsplash.com/photo-1507842217343-583f7270bfba?w=400&h=600&fit=crop",
    ],
    coverImage:
      "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&h=600&fit=crop",
  },
];

export default function BooksList() {
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);

  // TODO: Replace with actual API call
  // const { data: books } = useQuery({
  //   queryKey: ['books'],
  //   queryFn: async () => {
  //     const response = await fetch('http://localhost:8000/books');
  //     return response.json();
  //   },
  // });
  // const books = data?.data || [];

  const books = placeholderBooks;

  const handleAddToCart = async (
    e: React.MouseEvent<HTMLButtonElement>,
    book: Book
  ) => {
    e.stopPropagation();
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
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
        {books.map((book) => (
          <button
            key={book.id}
            onClick={() => setSelectedBook(book)}
            className="group flex flex-col gap-3 text-left transition-transform hover:scale-105 active:scale-95"
          >
            {/* Book Cover Image with Add to Cart Button */}
            <div className="relative h-64 sm:h-72 bg-gray-200 rounded-lg overflow-hidden shadow-md">
              <img
                src={book.coverImage}
                alt={book.title}
                className="w-full h-full object-cover group-hover:opacity-90 transition-opacity"
              />

              {/* Add to Cart Button - Floating in corner */}
              <button
                onClick={(e) => handleAddToCart(e, book)}
                className="absolute bottom-3 right-3 bg-green-600 hover:bg-green-700 text-white p-2.5 rounded-full shadow-lg transition-all hover:scale-110 active:scale-95 flex items-center justify-center"
                title="Add to cart"
              >
                <ShoppingCart className="w-5 h-5" />
              </button>
            </div>

            {/* Book Info */}
            <div className="flex flex-col gap-1">
              <h3 className="font-semibold text-base sm:text-lg text-gray-900 line-clamp-2">
                {book.title}
              </h3>
              <p className="text-sm text-gray-600">{book.author}</p>
              <span className="text-xs font-medium text-[#6750A4] bg-[#F3E5F5] px-2 py-1 rounded w-fit">
                {book.category}
              </span>
            </div>
          </button>
        ))}
      </div>

      <BookDetailModal book={selectedBook} onClose={() => setSelectedBook(null)} />
    </>
  );
}
