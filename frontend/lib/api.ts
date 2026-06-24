const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL;

function getAuthHeaders(): HeadersInit  {
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem(
          "access_token"
        )
      : null;

  return token
    ? {
        Authorization:
          `Bearer ${token}`,
      }
    : {};
}

export async function apiGet(
  endpoint: string
) {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      headers: {
        ...getAuthHeaders(),
      },
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error(
      `API Error: ${response.status}`
    );
  }

  return response.json();
}

export async function apiPost(
  endpoint: string,
  body: unknown
) {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
        ...getAuthHeaders(),
      },
      body: JSON.stringify(body),
    }
  );

  if (!response.ok) {
    throw new Error(
      `API Error: ${response.status}`
    );
  }

  return response.json();
}

export async function apiPut(
  endpoint: string,
  body: unknown
) {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      method: "PUT",
      headers: {
        "Content-Type":
          "application/json",
        ...getAuthHeaders(),
      },
      body: JSON.stringify(body),
    }
  );

  if (!response.ok) {
    throw new Error(
      `API Error: ${response.status}`
    );
  }

  return response.json();
}

export async function apiUpload(
  endpoint: string,
  formData: FormData
) {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      method: "POST",
      headers: {
        ...getAuthHeaders(),
      },
      body: formData,
    }
  );

  if (!response.ok) {
    throw new Error(
      `API Error: ${response.status}`
    );
  }

  return response.json();
}