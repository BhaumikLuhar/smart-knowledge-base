"use client";

import {
  useState,
} from "react";

import { useEffect } from "react";

import {
  useRouter,
} from "next/navigation";

import {
  login as loginRequest,
} from "@/services/auth-service";

import {
  useAuth,
} from "@/contexts/AuthContext";

export default function LoginPage() {

  const router = useRouter();

  const { login } = useAuth();

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [error, setError] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const {
    isAuthenticated
  } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, router]);

  async function handleSubmit(
    e: React.FormEvent
  ) {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {

      const result =
        await loginRequest(
          email,
          password
        );

      login(
        result.access_token,
        result.user
      );

      router.push(
        "/dashboard"
      );

    } catch {

      setError(
        "Invalid credentials"
      );

    } finally {

      setLoading(false);

    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">

      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md border rounded-lg p-8 space-y-6"
      >

        <div>
          <h1 className="text-2xl font-bold">
            Smart Knowledge Bank
          </h1>

          <p className="text-sm text-muted-foreground">
            Sign in to continue
          </p>
        </div>

        {error && (
          <div className="text-sm text-red-500">
            {error}
          </div>
        )}

        <div>
          <label className="block mb-2">
            Email
          </label>

          <input
            type="email"
            className="w-full border rounded px-3 py-2"
            value={email}
            onChange={(e) =>
              setEmail(
                e.target.value
              )
            }
          />
        </div>

        <div>
          <label className="block mb-2">
            Password
          </label>

          <input
            type="password"
            className="w-full border rounded px-3 py-2"
            value={password}
            onChange={(e) =>
              setPassword(
                e.target.value
              )
            }
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full border rounded py-2"
        >
          {loading
            ? "Signing in..."
            : "Login"}
        </button>

      </form>

    </div>
  );
}