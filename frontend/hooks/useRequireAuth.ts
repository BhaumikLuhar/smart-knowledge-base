"use client";

import {
  useEffect,
} from "react";

import {
  useRouter,
} from "next/navigation";

import {
  useAuth,
} from "@/contexts/AuthContext";

export function useRequireAuth() {

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
}