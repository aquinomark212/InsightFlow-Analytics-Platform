const API_URL = process.env.NEXT_PUBLIC_API_URL!;
const API_KEY = process.env.NEXT_PUBLIC_API_KEY!;

interface LoginPayload {
  username: string;
  password: string;
}

export async function getDashboard() {

  try {
    const res = await fetch(`${API_URL}/dashboard`, {
      headers: {
        "X-MY-SECRET-KEY": API_KEY,
      },
      credentials: "include",
      cache: "no-store",
    });

    console.log("Status:", res.status);
    const data = await res.json();
    console.log("Data:", data);
    return data;
  } catch (err) {
    console.error("Fetch error:", err);
    throw err;
  }
}

export async function login(data: LoginPayload) {

  const res = await fetch(`${API_URL}/login/`, {
    method: "POST",
    headers: {
      "X-MY-SECRET-KEY": API_KEY,
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify( data )
  });

  if (!res.ok){
     throw new Error(`Login request failed with status ${res.status}`);

  }
    console.log("API_URL:", API_URL);
    return res.json();
}


export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "X-MY-SECRET-KEY": API_KEY,
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    credentials: "include",
    cache: "no-store",
  });
  
  const data = await res.json().catch(() => ({}))

  if (res.status === 401) {
    throw new Error("Unauthorized");
  }

  if(!res.ok) {
    throw new Error(
      data?.detail ??
      data?.error ??
      `Request failed with status ${res.status}`
    );
  }

  return data
}
