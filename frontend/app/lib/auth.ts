const API_URL = process.env.NEXT_PUBLIC_API_URL!;
const API_KEY = process.env.NEXT_PUBLIC_API_KEY!;

export async function checkAuth() {
  const res = await fetch(`${API_URL}/dashboard/`, {
    headers: {
      "X-MY-SECRET-KEY": API_KEY,
    },
    credentials: "include",
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Request failed with status " + res.status);
  }

  return "Login Success";
}

export async function logout() {
  await fetch(`${API_URL}/logout/`, {
    method: "POST",
    credentials: "include",
  });

  window.location.href = "/login";
}
