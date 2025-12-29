import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight, X } from "lucide-react";

interface ImageLightboxProps {
  images: string[];
  onClose: () => void;
}

export default function ImageLightbox({ images, onClose }: ImageLightboxProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      } else if (e.key === "ArrowLeft") {
        previousImage();
      } else if (e.key === "ArrowRight") {
        nextImage();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [currentIndex]);

  const nextImage = () => {
    setCurrentIndex((prev) => (prev + 1) % images.length);
  };

  const previousImage = () => {
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  return (
    <div
      className="fixed inset-0 z-[9999] bg-black/80 flex items-center justify-center p-4"
      onClick={onClose}
    >
      {/* Content Container */}
      <div
        className="relative w-full max-w-4xl max-h-[90vh] flex flex-col items-center justify-center"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Image */}
        <img
          src={images[currentIndex]}
          alt={`Full view ${currentIndex + 1}`}
          className="max-w-full max-h-[80vh] object-contain"
        />

        {/* Navigation Arrows */}
        {images.length > 1 && (
          <>
            {/* Previous Button */}
            <button
              onClick={previousImage}
              className="absolute left-4 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/60 text-white p-3 rounded-full transition-colors z-10"
              title="Previous image (←)"
            >
              <ChevronLeft className="w-8 h-8" />
            </button>

            {/* Next Button */}
            <button
              onClick={nextImage}
              className="absolute right-4 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/60 text-white p-3 rounded-full transition-colors z-10"
              title="Next image (→)"
            >
              <ChevronRight className="w-8 h-8" />
            </button>

            {/* Image Counter */}
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black/40 text-white text-sm px-3 py-1.5 rounded-full">
              {currentIndex + 1} / {images.length}
            </div>
          </>
        )}

        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 bg-black/40 hover:bg-black/60 text-white p-2 rounded-full transition-colors z-10"
          title="Close (Esc)"
        >
          <X className="w-6 h-6" />
        </button>
      </div>
    </div>
  );
}
