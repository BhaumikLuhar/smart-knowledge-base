import "./globals.css";
import Sidebar from "@/components/sidebar";

export const metadata = {
  title: "Smart Knowledge Bank",
  description: "Enterprise Knowledge Intelligence Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="flex h-screen">
          <Sidebar />

          <main className="flex-1 overflow-auto p-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}