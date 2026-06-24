import { LoginResponse } from "@/types/auth";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL;

export async function login(
  email: string,
  password: string
): Promise<LoginResponse> {

  const response = await fetch(
    `${API_BASE_URL}/api/v1/auth/login`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        email,
        password,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      "Invalid email or password"
    );
  }

  return response.json();
}


export async function logoutRequest(
  token: string
) {

  await fetch(
    `${API_BASE_URL}/api/v1/auth/logout`,
    {
      method: "POST",
      headers: {
        Authorization:
          `Bearer ${token}`,
      },
    }
  );

}