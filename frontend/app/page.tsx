import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-6 text-center text-foreground">
      <div className="max-w-xl space-y-6">
        <p className="text-sm font-semibold uppercase tracking-[0.35em] text-accent-deep/70">
          InsightFlow Analytics
        </p>
        <h1 className="text-5xl font-semibold tracking-[-0.05em] text-balance">
          The front door is ready.
        </h1>
        <p className="text-base leading-7 text-foreground/70 sm:text-lg">
          Head to the login screen to access the workspace and continue into the
          dashboard.
        </p>
        <div className="flex justify-center">
          <Link
            href="/login"
            className="rounded-full bg-accent px-6 py-3 text-sm font-semibold uppercase tracking-[0.2em] text-white transition hover:bg-accent-deep"
          >
            Open Login Page
          </Link>
        </div>
      </div>
    </main>
  );
}
