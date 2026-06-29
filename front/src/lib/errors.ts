interface FastApiValidationItem {
  loc?: unknown[];
  msg?: unknown;
}

function formatValidationItem(item: unknown): string {
  if (typeof item === "string") return item;
  if (typeof item === "object" && item !== null && "msg" in item) {
    const { msg, loc } = item as FastApiValidationItem;
    const path =
      Array.isArray(loc) && loc.length > 1
        ? `${loc
            .slice(1)
            .map(String)
            .join(".")}: `
        : "";
    if (typeof msg === "string") return `${path}${msg}`;
  }
  try {
    return JSON.stringify(item);
  } catch {
    return "Error de validacion.";
  }
}

export function extractApiMessage(error: unknown): string {
  if (typeof error === "object" && error !== null && "response" in error) {
    const response = (error as {
      response?: { status?: number; data?: { detail?: unknown } };
    }).response;
    const detail = response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail.map(formatValidationItem).join("; ");
    }
    if (detail && typeof detail === "object") {
      try {
        return JSON.stringify(detail);
      } catch {
        // fallthrough
      }
    }
    if (response?.status) {
      return `Error HTTP ${response.status}.`;
    }
  }
  if (error instanceof Error) return error.message;
  return "Error desconocido.";
}
