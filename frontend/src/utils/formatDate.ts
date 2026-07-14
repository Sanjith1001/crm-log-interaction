export function formatDate(value: string | Date) {
  return new Intl.DateTimeFormat("en").format(new Date(value));
}

