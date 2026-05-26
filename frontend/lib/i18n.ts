import { en } from "./dictionaries/en";
import { zh } from "./dictionaries/zh";
import type { Locale } from "./types";

export const dictionaries = { en, zh };
export function getDictionary(locale: string) {
  return dictionaries[(locale === "zh" ? "zh" : "en") as Locale];
}
