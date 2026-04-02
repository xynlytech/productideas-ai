import posthog from "posthog-js";

const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY || "";
const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST || "https://us.i.posthog.com";

let initialized = false;

export function initAnalytics() {
  if (initialized || typeof window === "undefined" || !POSTHOG_KEY) return;
  posthog.init(POSTHOG_KEY, {
    api_host: POSTHOG_HOST,
    capture_pageview: true,
    capture_pageleave: true,
    persistence: "localStorage+cookie",
  });
  initialized = true;
}

export function identifyUser(userId: number, email: string, name: string) {
  if (!POSTHOG_KEY) return;
  posthog.identify(String(userId), { email, name });
}

export function resetAnalytics() {
  if (!POSTHOG_KEY) return;
  posthog.reset();
}

type EventName =
  | "signup"
  | "login"
  | "logout"
  | "idea_viewed"
  | "idea_saved"
  | "idea_unsaved"
  | "note_added"
  | "export_started"
  | "alert_created"
  | "alert_deleted"
  | "filter_used"
  | "search_used"
  | "sort_changed";

export function trackEvent(event: EventName, properties?: Record<string, unknown>) {
  if (!POSTHOG_KEY) return;
  posthog.capture(event, properties);
}
