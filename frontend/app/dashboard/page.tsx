"use client";
import Link from "next/link";
import { apiFetch } from "../lib/api";
import { useEffect, useState } from "react";
import { checkAuth, logout } from "../lib/auth";
import { useRouter } from "next/navigation";
import PredictionChart from "../components/PredictionChart";

type DashboardEventPoint = {
  date: string;
  count: number;
};

type TopEventType = {
  event_type: string;
  count: number;
};

type RecentEvent = {
  id: number | string;
  event_type: string;
  timestamp: string;
};

type DashboardData = {
  total_events: number;
  events_per_day: DashboardEventPoint[];
  top_event_types: TopEventType[];
  recent_events: RecentEvent[];
  date_range: {
    start: string | null;
    end: string | null;
  };
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function getPeakDay(points: DashboardEventPoint[]) {
  if (!points.length) {
    return null;
  }

  return points.reduce((max, point) => (point.count > max.count ? point : max));
}

function getAveragePerDay(points: DashboardEventPoint[]) {
  if (!points.length) {
    return 0;
  }

  const total = points.reduce((sum, point) => sum + point.count, 0);
  return Math.round(total / points.length);
}

function toRecentEvent(value: unknown): RecentEvent | null {
  if (!value || typeof value !== "object") {
    return null;
  }

  const event = value as Partial<RecentEvent> & { created_at?: string };

  if (typeof event.event_type !== "string") {
    return null;
  }

  const timestamp =
    typeof event.timestamp === "string"
      ? event.timestamp
      : typeof event.created_at === "string"
        ? event.created_at
        : new Date().toISOString();

  return {
    id: event.id ?? `${event.event_type}-${timestamp}`,
    event_type: event.event_type,
    timestamp,
  };
}

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  // const [events, setEvents] = useState<RecentEvent[]>([]);
  const [data, setData] = useState<number[]>([]);
  const [prediction, setPrediction] = useState<number>(0);
  const [loadingPrediction, setLoadingPrediction] = useState(true);

  const router = useRouter();

  const fetchPrediction = async () => {
    try {
      setLoadingPrediction(true);

      const res = await apiFetch("/ml/predict/");

      setData(res.historical_data ?? []);
      setPrediction(res.prediction_next_day ?? 0);
    } catch (err) {
      console.error("Error fetching prediction:", err);
      setData([]);
      setPrediction(0);
    } finally {
      setLoadingPrediction(false);
    }
  };

  useEffect(() => {
    fetchPrediction();
  }, []);

  useEffect(() => {
    console.log(data);
    console.log(prediction);
  }, [data, prediction]);

  useEffect(() => {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws/dashboard/");

    socket.onopen = () => {
      console.log("WebSocket connected");
    };

    socket.onmessage = (messageEvent) => {
      const data = JSON.parse(messageEvent.data);

      if (data.type === "alert") {
        alert(data.data.message);
        console.log("🚨 ALERT:", data.data);
      }

      if (data.type === "dashboard_update") {
        const newEvent = toRecentEvent(data.data);
        if (!newEvent) {
          return;
        }

        // setEvents((prev) => [newEvent, ...prev]);

        setDashboard((prev) =>
          prev
            ? {
                ...prev,
                total_events: prev.total_events + 1,
                recent_events: [newEvent, ...prev.recent_events].slice(0, 10),
              }
            : prev,
        );
      }

      console.log("Message:", data);
    };

    socket.onclose = () => {
      console.log("WebSocket disconnected");
    };

    return () => {
      socket.close();
    };
  }, []);

  useEffect(() => {
    async function validate() {
      try {
        const data = await checkAuth();
        console.log(data);
      } catch {
        router.push("/login");
      }
    }

    validate();
  }, []);

  useEffect(() => {
    apiFetch("/dashboard")
      .then((data) => {
        setDashboard({
          ...data,
          events_per_day: data.events_per_day ?? [],
          top_event_types: data.top_event_types ?? [],
          recent_events: data.recent_events ?? [],
        });
      })
      .catch(() => setError("Could not load dashboard data."))
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading dashboard...</p>;

  if (error) return <p>{error}</p>;

  const handleLogout = async () => {
    await logout();
  };

  const peakDay = dashboard?.events_per_day
    ? getPeakDay(dashboard.events_per_day)
    : null;
  const avgPerDay = dashboard?.events_per_day
    ? getAveragePerDay(dashboard.events_per_day)
    : 0;
  const topType = dashboard?.top_event_types?.[0] ?? null;
  const maxDailyCount = Math.max(
    ...(dashboard?.events_per_day.map((item) => item.count) ?? [1]),
  );

  // const recentEvents = [...events, ...(dashboard?.recent_events ?? [])];

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,#12344a_0%,#08131d_48%,#04070b_100%)] px-6 py-8 text-zinc-50">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <header className="rounded-[28px] border border-white/10 bg-white/6 p-6 backdrop-blur-xl">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-3">
              <p className="text-xs font-semibold uppercase tracking-[0.35em] text-cyan-300">
                InsightFlow
              </p>
              <h1 className="text-4xl font-semibold tracking-[-0.04em] sm:text-5xl">
                Event analytics dashboard
              </h1>
              <p className="max-w-2xl text-sm leading-6 text-zinc-300 sm:text-base">
                A live view of event volume, activity trends, and recent product
                behavior.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <div className="rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-200">
                {error ? "Waiting for data" : "Live snapshot"}
              </div>
              <Link
                href="/login"
                className="rounded-full border border-white/12 bg-white/8 px-4 py-2 text-sm text-zinc-100 transition hover:bg-white/14"
              >
                Back to login
              </Link>
            </div>
          </div>
        </header>

        {error ? (
          <section className="rounded-[24px] border border-rose-400/30 bg-rose-400/10 px-5 py-4 text-sm text-rose-100">
            {error}
          </section>
        ) : null}

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <article className="rounded-[24px] border border-white/10 bg-white/6 p-5 backdrop-blur-xl">
            <p className="text-sm text-zinc-400">Total events</p>
            <p className="mt-5 text-3xl font-semibold tracking-tight">
              {error ? "--" : (dashboard?.total_events ?? 0)}
            </p>
            <p className="mt-3 text-xs uppercase tracking-[0.2em] text-zinc-500">
              Full filtered range
            </p>
          </article>

          <article className="rounded-[24px] border border-white/10 bg-white/6 p-5 backdrop-blur-xl">
            <p className="text-sm text-zinc-400">Average per day</p>
            <p className="mt-5 text-3xl font-semibold tracking-tight">
              {error ? "--" : avgPerDay}
            </p>
            <p className="mt-3 text-xs uppercase tracking-[0.2em] text-zinc-500">
              Across visible days
            </p>
          </article>

          <article className="rounded-[24px] border border-white/10 bg-white/6 p-5 backdrop-blur-xl">
            <p className="text-sm text-zinc-400">Top event type</p>
            <p className="mt-5 text-2xl font-semibold tracking-tight">
              {error ? "--" : (topType?.event_type ?? "No events yet")}
            </p>
            <p className="mt-3 text-xs uppercase tracking-[0.2em] text-zinc-500">
              {error ? "--" : `${topType?.count ?? 0} matching events`}
            </p>
          </article>

          <article className="rounded-[24px] border border-white/10 bg-white/6 p-5 backdrop-blur-xl">
            <p className="text-sm text-zinc-400">Peak day</p>
            <p className="mt-5 text-2xl font-semibold tracking-tight">
              {error ? "--" : peakDay ? formatDate(peakDay.date) : "No data"}
            </p>
            <p className="mt-3 text-xs uppercase tracking-[0.2em] text-zinc-500">
              {error
                ? "--"
                : peakDay
                  ? `${peakDay.count} events`
                  : "Waiting for activity"}
            </p>
          </article>
        </section>

        <section className="grid gap-4 xl:grid-cols-[1.5fr_0.95fr]">
          <article className="rounded-[28px] border border-white/10 bg-white/6 p-6 backdrop-blur-xl">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm text-cyan-200">Events per day</p>
                <h2 className="mt-2 text-2xl font-semibold tracking-tight">
                  Activity trend
                </h2>
              </div>
              <span className="rounded-full bg-cyan-400/10 px-3 py-1 text-xs text-cyan-100">
                Backend-aligned
              </span>
            </div>

            <div className="mt-8">
              {dashboard?.events_per_day?.length ? (
                <div className="flex h-64 items-end gap-3">
                  {dashboard.events_per_day.map((point) => (
                    <div
                      key={point.date}
                      className="flex flex-1 flex-col items-center gap-3"
                    >
                      <div className="flex h-52 w-full items-end">
                        <div
                          className="w-full rounded-t-2xl bg-gradient-to-t from-cyan-500 via-sky-400 to-cyan-200"
                          style={{
                            height: `${Math.max(
                              12,
                              (point.count / maxDailyCount) * 100,
                            )}%`,
                          }}
                        />
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-zinc-300">
                          {formatDate(point.date)}
                        </p>
                        <p className="mt-1 text-xs text-zinc-500">
                          {point.count}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="rounded-[24px] border border-white/8 bg-black/10 p-6 text-sm text-zinc-400">
                  No daily event data available yet.
                </div>
              )}
            </div>
          </article>

          <div className="grid gap-4">
            <article className="rounded-[28px] border border-white/10 bg-white/6 p-6 backdrop-blur-xl">
              <p className="text-sm text-zinc-400">Top event types</p>
              <div className="mt-5 space-y-4">
                {dashboard?.top_event_types?.length ? (
                  dashboard.top_event_types.slice(0, 5).map((item) => (
                    <div key={item.event_type} className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-zinc-200">{item.event_type}</span>
                        <span className="text-zinc-400">{item.count}</span>
                      </div>
                      <div className="h-2 rounded-full bg-white/8">
                        <div
                          className="h-2 rounded-full bg-gradient-to-r from-emerald-300 to-cyan-400"
                          style={{
                            width: `${Math.max(
                              10,
                              (item.count /
                                (dashboard.top_event_types[0]?.count || 1)) *
                                100,
                            )}%`,
                          }}
                        />
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-zinc-500">
                    No event type data available.
                  </p>
                )}
              </div>
            </article>

            <article className="rounded-[28px] border border-white/10 bg-white/6 p-6 backdrop-blur-xl">
              <p className="text-sm text-zinc-400">Recent events</p>
              <div className="mt-5 space-y-3">
                {dashboard?.recent_events?.length ? (
                  dashboard.recent_events.slice(0, 10).map((event) => (
                    <div
                      key={event.id}
                      className="rounded-[20px] border border-white/8 bg-black/10 p-4"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <h3 className="text-sm font-medium text-zinc-100">
                          {event.event_type}
                        </h3>
                        <span className="text-xs text-zinc-500">
                          #{event.id}
                        </span>
                      </div>
                      <p className="mt-2 text-sm text-zinc-400">
                        {formatDateTime(event.timestamp)}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-zinc-500">No recent events yet.</p>
                )}
              </div>
            </article>
          </div>
        </section>
      </div>
      {loadingPrediction ? (
        <p>Loading prediction...</p>
      ) : (
        <div>
          <PredictionChart data={data} prediction={prediction} />
        </div>
      )}

      <button type="submit" onClick={handleLogout}>
        Logout
      </button>
    </main>
  );
}
