import { Link } from "react-router-dom";

export default function Header({ onOpenUpload }: { onOpenUpload?: () => void }) {
  return (
    <header className="w-full bg-white">
      <div className="h-3 bg-black" />

      <div className="flex items-center justify-between px-4 sm:px-8 lg:px-20 py-3 sm:py-4">
        <Link
          to="/"
          className="flex items-center justify-center px-8 sm:px-12 py-4 sm:py-6 bg-white rounded-[21px] font-bold text-base text-black hover:opacity-80 transition-opacity"
        >
          Главная
        </Link>

        <div className="flex items-center gap-2 sm:gap-4">
          <Link
            to="/account"
            className="flex items-center justify-center px-4 sm:px-5 py-2 sm:py-3 bg-[#FEF3F2] rounded-[9px] font-bold text-base text-[#6750A4] hover:opacity-80 transition-opacity whitespace-nowrap"
          >
            Аккаунт
          </Link>

          <button
            onClick={() => onOpenUpload && onOpenUpload()}
            className="flex items-center justify-center px-4 sm:px-5 py-2 sm:py-3 bg-[#FEF3F2] rounded-[9px] font-bold text-base text-[#B42318] hover:opacity-80 transition-opacity whitespace-nowrap"
          >
            Загрузить книгу
          </button>
        </div>
      </div>

      <div className="h-0.5 bg-black" />
    </header>
  );
}
