export default function Placeholder({ title }: { title: string }) {
  return (
    <div className="min-h-screen bg-white">
      <main className="container mx-auto px-4 sm:px-8 py-12 sm:py-16">
        <div className="text-center max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">{title}</h1>
          <p className="text-gray-600">
            This page is under construction. Continue prompting to add content here.
          </p>
        </div>
      </main>
    </div>
  );
}
