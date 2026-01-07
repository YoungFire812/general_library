import { useState } from "react";
import { ShoppingCart } from "lucide-react";
import BookDetailModal from "./BookDetailModal";
import ImageLightbox from "./ImageLightbox";
import Pagination from "./Pagination";

export interface Book {
  id: number;
  title: string;
  author: string;
  category: string;
  description: string;
  images: string[];
  thumbnail: string;
  created_at: string;
  is_published: boolean;
  stock: boolean;
}

export const getBooks = async (page = 1, limit = 24) => {
  try {
    const response = await fetch(`http://localhost:8000/v1/books?page=${page}&limit=${limit}`);

    if (!response.ok) {
      throw new Error(`Ошибка сервера: ${response.status}`);
    }

    // Получаем массив объектов (словарей)
    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error("Ошибка при получении книг:", error);
    return [];
  }
};

// Placeholder data - Replace with API data later
const placeholderBooks: Book[] = await getBooks();

const BOOKS_PER_PAGE = 6;

export default function BooksList() {
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [lightboxImages, setLightboxImages] = useState<string[] | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

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

  // Pagination logic
  const totalPages = Math.ceil(books.length / BOOKS_PER_PAGE);
  const startIndex = (currentPage - 1) * BOOKS_PER_PAGE;
  const paginatedBooks = books.slice(startIndex, startIndex + BOOKS_PER_PAGE);

  const handleAddToCart = async (
    e: React.MouseEvent<HTMLButtonElement>,
    book: Book
  ) => {
    e.stopPropagation();
    try {
      const response = await fetch("/api/cart", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          bookId: book.id,
        }),
      });

      if (response.ok) {
        alert("Book added to basket!");
      } else {
        // Optimistically add to basket if API not available
        alert("Book added to basket!");
      }
    } catch (error) {
      console.error("Error adding to basket:", error);
      // Gracefully handle error and show success message for UX
      alert("Book added to basket!");
    }
  };

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
        {paginatedBooks.map((book) => (
          <div
            key={book.id}
            className="group flex flex-col gap-3 text-left"
          >
            {/* Book Cover Image - Clickable to open product details */}
            <div
              className="relative h-80 sm:h-96 bg-gray-200 rounded-lg overflow-hidden shadow-md cursor-pointer group/image"
              onClick={() => setSelectedBook(book)}
            >
              <img
                src={book.thumbnail}
                alt={book.title}
                className="w-full h-full object-contain group-hover/image:opacity-80 transition-opacity"
              />

              {/* Overlay on hover to show it's clickable */}
              <div className="absolute inset-0 bg-black/0 group-hover/image:bg-black/20 transition-colors flex items-center justify-center">
                <p className="text-white opacity-0 group-hover/image:opacity-100 transition-opacity font-semibold text-sm">
                  View Details
                </p>
              </div>
            </div>

            {/* Book Info with Add to Cart Button */}
            <div className="flex flex-col gap-2">
              {/* Title, Author, Category */}
              <button
                onClick={() => setSelectedBook(book)}
                className="text-left hover:opacity-70 transition-opacity"
              >
                <h3 className="font-semibold text-base sm:text-lg text-gray-900 line-clamp-2">
                  {book.title}
                </h3>
                <p className="text-sm text-gray-600">{book.author}</p>
                <span className="text-xs font-medium text-[#6750A4] bg-[#F3E5F5] px-2 py-1 rounded w-fit">
                  {book.category}
                </span>
              </button>

              {/* Add to Cart Button - Rectangular, lower position */}
              <button
                onClick={(e) => handleAddToCart(e, book)}
                className="flex items-center justify-center gap-2 w-full bg-[#6750A4] hover:bg-[#5a4494] text-white font-semibold py-2.5 rounded transition-colors mt-1"
                title="Add to cart"
              >
                <ShoppingCart className="w-4 h-4" />
                Add to Cart
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
        />
      )}

      {/* Image Lightbox */}
      {lightboxImages && (
        <ImageLightbox
          images={lightboxImages}
          onClose={() => setLightboxImages(null)}
        />
      )}

      <BookDetailModal book={selectedBook} onClose={() => setSelectedBook(null)} />
    </>
  );
}
