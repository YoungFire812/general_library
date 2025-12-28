import BooksList from "@/components/BooksList";

export default function Index() {
  return (
    <div className="min-h-screen bg-white">
      <main className="container mx-auto px-4 sm:px-8 py-12 sm:py-16">
        <div className="flex flex-col gap-8">
          {/* Page Header */}
          <div className="flex flex-col gap-2">
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Available Books
            </h1>
            <p className="text-base text-gray-600">
              Browse and exchange books from our community library
            </p>
          </div>

          {/* Books Grid */}
          <BooksList />
        </div>
      </main>
    </div>
  );
}
