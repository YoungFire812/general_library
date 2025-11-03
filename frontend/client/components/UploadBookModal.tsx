import React, { useRef, useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import { toast as sonnerToast } from "sonner";

export default function UploadBookModal({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [author, setAuthor] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const contentRef = useRef<HTMLDivElement | null>(null);
  const titleRef = useRef<HTMLInputElement | null>(null);
  const descriptionRef = useRef<HTMLTextAreaElement | null>(null);
  const authorRef = useRef<HTMLInputElement | null>(null);
  const { toast } = useToast();
  const API = "http://localhost:8000/v1";

  const uploadFiles = async (files: File[]): Promise<string[]> => {
    if (files.length === 0) return [];

    const fd = new FormData();
    files.forEach((file) => fd.append("files", file)); // имя "files" должно совпадать с параметром FastAPI

    const res = await fetch(`${API}/upload-files`, {
      method: "POST",
      body: fd,
    });

    if (!res.ok) throw new Error(`Failed to upload files: ${res.status}`);

    const data = await res.json();
    return data.data.files;
  };

  useEffect(() => {
    if (!open) {
      setTitle("");
      setDescription("");
      setAuthor("");
      setFiles([]);
      setErrors([]);
    } else {
      // focus the title and ensure modal content is scrolled to top
      setTimeout(() => {
        titleRef.current?.focus();
        contentRef.current?.scrollTo({ top: 0, behavior: "smooth" });
      }, 50);
    }
  }, [open]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    if (open) window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFiles = Array.from(e.target.files || []);
    const combined = [...files, ...newFiles];
    
    if (combined.length > 5) {
      toast({ 
        title: "Too many files", 
        description: "Maximum 5 photos allowed",
        type: "destructive" 
      });
      return;
    }
    
    setFiles(combined);
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const validate = () => {
    const errs: string[] = [];
    if (!title.trim()) errs.push("Title is required");
    if (!description.trim()) errs.push("Description is required");
    if (!author.trim()) errs.push("Author is required");
    if (files.length === 0) errs.push("Please upload at least one photo");
    setErrors(errs);

    if (errs.length > 0) {
      // focus and scroll to first invalid field
      if (!title.trim()) {
        titleRef.current?.focus();
        titleRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
      } else if (!description.trim()) {
        descriptionRef.current?.focus();
        descriptionRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
      } else if (!author.trim()) {
        authorRef.current?.focus();
        authorRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
      } else if (files.length === 0) {
        const el = contentRef.current?.querySelector("[aria-label='Upload photos']") as HTMLElement | null;
        el?.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }

    return errs.length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) {
      toast({ title: "Validation error", description: "Please fill all fields", type: "destructive" });
      return;
    }

    try {
      const photosUrls = await uploadFiles(files);
      const bookData = {
        title,
        author,
        description,
        stock: true,
        thumbnail: photosUrls[0],
        images: photosUrls,
        is_published: true,
        created_at: new Date().toISOString(),
        category_id: 4,
      };

      const res = await fetch(`${API}/books`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(bookData),
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      // Prefer exact success handling: if server replies OK, ensure modal closes and show a green toast
      if (res.ok) {
        sonnerToast.success("Book uploaded successfully");
        // close modal; call twice to be resilient during HMR or race conditions
        try {
          onClose();
          setTimeout(() => onClose(), 300);
        } catch (e) {
          /* ignore */
        }
        return;
      }

      throw new Error(`Server error: ${res.status}`);
    } catch (err) {
      console.error(err);
      toast({ title: "Upload failed", description: "There was an error uploading the book", type: "destructive" });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6">
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
        aria-hidden
      />

      <div ref={contentRef} className="relative z-10 w-full max-w-2xl bg-white rounded-lg shadow-xl border border-slate-200 max-h-[calc(100vh-96px)] overflow-auto">
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h3 className="text-lg font-semibold">Загрузить книгу</h3>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-700"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Название</label>
            <input
              ref={titleRef}
              className="w-full rounded-md border px-3 py-2 outline-none focus:ring-2 focus:ring-[#6750A4]"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Введите название книги"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Описание</label>
            <textarea
              ref={descriptionRef}
              className="w-full rounded-md border px-3 py-2 outline-none focus:ring-2 focus:ring-[#6750A4] min-h-[80px]"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Краткое описание"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Автор</label>
            <input
              ref={authorRef}
              className="w-full rounded-md border px-3 py-2 outline-none focus:ring-2 focus:ring-[#6750A4]"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              placeholder="Имя автора"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Фото книги ({files.length}/5)</label>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              className="hidden"
              onChange={handleFileSelect}
            />

            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={files.length >= 5}
              className="flex items-center justify-center w-32 h-32 border-2 border-dashed border-slate-300 rounded-md text-slate-400 hover:border-slate-400 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Upload photos"
            >
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="3" y="3" width="18" height="18" rx="2" stroke="#CBD5E1" strokeWidth="1.5" fill="none" />
                <path d="M8 12H16" stroke="#CBD5E1" strokeWidth="1.5" strokeLinecap="round" />
                <path d="M12 8V16" stroke="#CBD5E1" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </button>

            {files.length > 0 && (
              <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-3">
                {files.map((file, idx) => (
                  <div key={idx} className="relative group">
                    <img
                      src={URL.createObjectURL(file)}
                      alt={`preview-${idx}`}
                      className="w-full h-24 object-cover rounded-md border"
                    />
                    <button
                      type="button"
                      onClick={() => removeFile(idx)}
                      className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                      aria-label="Remove photo"
                    >
                      ✕
                    </button>
                    <div className="text-xs text-slate-600 mt-1 truncate">{file.name}</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {errors.length > 0 && (
            <div className="bg-red-50 text-red-700 p-3 rounded">
              <ul className="list-disc pl-5">
                {errors.map((e) => (
                  <li key={e}>{e}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex items-center justify-end gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-md border hover:bg-slate-50"
            >
              Отмена
            </button>
            <button
              onClick={handleSubmit}
              className="px-4 py-2 rounded-md bg-[#6750A4] text-white font-semibold hover:opacity-90"
            >
              Загрузить книгу
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
