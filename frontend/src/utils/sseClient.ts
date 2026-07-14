export function createSseClient(url: string) {
  return new EventSource(url);
}

