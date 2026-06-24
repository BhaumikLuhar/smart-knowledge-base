import "./globals.css";

import {
  AuthProvider,
} from "@/contexts/AuthContext";

export const metadata = {
  title: "Smart Knowledge Bank",
  description:
    "Enterprise Knowledge Intelligence Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}