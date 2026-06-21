const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL;

export async function apiGet(
  endpoint: string
) {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      headers: {
        "X-Admin-Token":
            "dev-token"
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

        "X-Admin-Token": 
            "dev-token",
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
        "X-Admin-Token":
            "dev-token",
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