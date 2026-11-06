const baseUrl = import.meta.env.BASE_URL;

export const cfpUrl = "https://cfp.pycon.cz/2027/cfp";
export const cfpEmail = "info@pycon.cz";

export const cfpPages = {
  cfp: `${baseUrl}cfp/`,
  guide: `${baseUrl}cfp/guide/`,
  guideCs: `${baseUrl}cfp/pruvodce/`,
};

/** Last day for submissions, 23:59 Anywhere on Earth (UTC−12). Change only this date. */
const deadlineDate = "2027-01-17";

// Formatted in UTC, so the build machine's time zone can't shift the day
const formatDate = (locale: string) =>
  new Intl.DateTimeFormat(locale, { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }).format(
    new Date(`${deadlineDate}T00:00:00Z`),
  );

export const cfpDeadline = {
  /** For <time datetime>: 23:59 at UTC−12 */
  datetime: `${deadlineDate}T23:59-12:00`,
  en: formatDate("en-GB"),
  cs: formatDate("cs-CZ"),
};

/** Conference days for each format, shown on the CFP page and the homepage */
export const formatDays = { talks: "17–18 April", workshops: "16 April" };

export interface Track {
  name: string;
  topics: string;
  color?: "lavender" | "lime" | "pink";
}

export const tracks: Track[] = [
  {
    name: "Python Core and Tooling",
    topics: "Internals, extensions, packaging, developer productivity, testing, QA, and security.",
  },
  {
    name: "Web, Infrastructure, and Hardware",
    topics: "Web and APIs, front-end integration, DevOps, cloud, IoT, and embedded systems.",
    color: "lavender",
  },
  {
    name: "Community and People",
    topics:
      "Community building, education, ethics, legal, sustainability, careers, leadership, and games, art, and play.",
    color: "lime",
  },
  {
    name: "PyData: Data, Science, and AI",
    topics:
      "ML research and applications, NLP and computer vision, data preparation and visualization, Jupyter, scientific Python, data engineering, and MLOps.",
    color: "pink",
  },
];
