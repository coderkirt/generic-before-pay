"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  void error;
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          fontFamily: "system-ui, sans-serif",
          fontSize: "18px",
          color: "#0b0c0c",
          background: "#ffffff",
          padding: "1.5rem",
        }}
      >
        <h1>Something went wrong</h1>
        <p>You can try again, or start again. Nothing from this screen is kept.</p>
        <button
          type="button"
          onClick={reset}
          style={{ minHeight: "44px", font: "inherit", fontWeight: 700, padding: "0.5rem 1rem" }}
        >
          Try again
        </button>
      </body>
    </html>
  );
}
