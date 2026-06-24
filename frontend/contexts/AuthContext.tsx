"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import { AuthUser } from "@/types/auth";

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  login: (token: string, user: AuthUser) => void;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext =
  createContext<AuthContextType | null>(
    null
  );

export function AuthProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [user, setUser] =
    useState<AuthUser | null>(
      null
    );

  const [token, setToken] =
    useState<string | null>(
      null
    );

  useEffect(() => {
    const savedToken =
      localStorage.getItem(
        "access_token"
      );

    const savedUser =
      localStorage.getItem(
        "user"
      );

    if (
      savedToken &&
      savedUser
    ) {
      setToken(savedToken);
      setUser(
        JSON.parse(savedUser)
      );
    }
  }, []);

  function login(
    token: string,
    user: AuthUser
  ) {
    localStorage.setItem(
      "access_token",
      token
    );

    localStorage.setItem(
      "user",
      JSON.stringify(user)
    );

    setToken(token);
    setUser(user);
  }

  async function logout() {

    const token =
      localStorage.getItem(
        "access_token"
      );

    if (token) {

      try {

        const {
          logoutRequest,
        } = await import(
          "@/services/auth-service"
        );

        await logoutRequest(
          token
        );

      } catch {
        // ignore
      }
    }

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user"
    );

    setToken(null);

    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isAuthenticated:
          !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {
  const context =
    useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}