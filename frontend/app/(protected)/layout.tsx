"use client";

import {
  useEffect,
} from "react";

import {
  useRouter,
} from "next/navigation";

import Sidebar from "@/components/sidebar";

import {
  useAuth,
} from "@/contexts/AuthContext";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {

  const router =
    useRouter();

  const {
    isAuthenticated,
  } = useAuth();

  useEffect(() => {

    if (
      !isAuthenticated
    ) {
      router.replace(
        "/login"
      );
    }

  }, [
    isAuthenticated,
    router,
  ]);

  if (
    !isAuthenticated
  ) {
    return null;
  }

  return (
    <div className="flex h-screen">

      <Sidebar />

      <main className="flex-1 overflow-auto p-8">
        {children}
      </main>

    </div>
  );
}