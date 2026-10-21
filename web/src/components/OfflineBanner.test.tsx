import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OfflineBanner } from "@/components/OfflineBanner";
import { OFFLINE_MESSAGE } from "@/lib/copy/approved";
import { TODO_NEEDS_HUMAN_REVIEW } from "@/lib/i18n/placeholder";
import { renderApp } from "@/test/render";

describe("OfflineBanner", () => {
  it("stays quiet while online", () => {
    renderApp(<OfflineBanner offline={false} />);
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("shows the offline sentence without the review token", () => {
    renderApp(<OfflineBanner offline />);
    const status = screen.getByRole("status");
    expect(status).toHaveTextContent(OFFLINE_MESSAGE);
    expect(status).not.toHaveTextContent(TODO_NEEDS_HUMAN_REVIEW);
  });
});
