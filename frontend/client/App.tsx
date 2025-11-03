import "./global.css";

import { Toaster } from "@/components/ui/toaster";
import { createRoot } from "react-dom/client";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Index from "./pages/Index";
import Placeholder from "./pages/Placeholder";
import NotFound from "./pages/NotFound";
import { useState } from "react";
import UploadBookModal from "./components/UploadBookModal";

const queryClient = new QueryClient();

function AppContent() {
  const [openUpload, setOpenUpload] = useState(false);
  return (
    <>
      <Header onOpenUpload={() => setOpenUpload(true)} />
      <UploadBookModal open={openUpload} onClose={() => setOpenUpload(false)} />

      <Routes>
        <Route path="/" element={<Index />} />
        <Route path="/account" element={<Placeholder title="Аккаунт" />} />
        <Route path="/upload" element={<Placeholder title="Загрузить книгу" />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </>
  );
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

const container = document.getElementById("root");
// Prevent createRoot being called multiple times during HMR
declare global {
  interface Window {
    __react_root__?: import("react-dom/client").Root;
  }
}
if (container) {
  if (!window.__react_root__) {
    window.__react_root__ = createRoot(container);
  }
  window.__react_root__.render(<App />);
}
