interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({
  currentPage,
  totalPages,
  onPageChange,
}: PaginationProps) {
  const pageNumbers = [];

  for (let i = 1; i <= totalPages; i++) {
    pageNumbers.push(i);
  }

  return (
    <div className="flex items-center justify-center gap-2 mt-8 pb-8">
      {pageNumbers.map((page) => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          className={`px-3 py-2 rounded-lg font-semibold transition-colors ${
            currentPage === page
              ? "bg-[#6750A4] text-white"
              : "bg-gray-200 text-gray-900 hover:bg-gray-300"
          }`}
        >
          {page}
        </button>
      ))}
    </div>
  );
}
