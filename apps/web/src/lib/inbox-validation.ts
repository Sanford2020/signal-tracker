export const EMPTY_SUBMISSION_MESSAGE =
  "Enter a URL, title, or pasted content before submitting.";

export function hasSubmissionInput(
  url: string,
  title: string,
  content: string,
): boolean {
  return [url, title, content].some((value) => value.trim().length > 0);
}

type ValidationDetail = {
  msg?: string;
  loc?: (string | number)[];
};

type ErrorBody = {
  success?: boolean;
  error?: { code?: string; message?: string };
  detail?: string | ValidationDetail[] | { message?: string };
};

export function extractErrorMessage(body: unknown, status: number): string {
  if (!body || typeof body !== "object") {
    return `Request failed: ${status}`;
  }

  const payload = body as ErrorBody;

  if (payload.error?.message) {
    return payload.error.message;
  }

  if (typeof payload.detail === "string") {
    return payload.detail;
  }

  if (Array.isArray(payload.detail) && payload.detail.length > 0) {
    return payload.detail
      .map((item) => item.msg?.replace(/^Value error,\s*/i, "") ?? "Validation error.")
      .join(" ");
  }

  if (
    payload.detail &&
    typeof payload.detail === "object" &&
    "message" in payload.detail &&
    typeof payload.detail.message === "string"
  ) {
    return payload.detail.message;
  }

  return `Request failed: ${status}`;
}
