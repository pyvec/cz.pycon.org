const baseUrl = import.meta.env.BASE_URL;

export const menuItems = [
  { label: "Home", href: baseUrl },
  { label: "Sponsorship", href: `${baseUrl}sponsorship/` },
  { label: "Volunteer", href: `${baseUrl}volunteer/` },
  { label: "Code of Conduct", href: `${baseUrl}coc/` },
];

export const socialLinks = [
  { label: "X (formerly Twitter)", shortLabel: "X (Twitter)", href: "https://x.com/pyconcz", icon: "x" },
  { label: "Mastodon", shortLabel: "Mastodon", href: "https://floss.social/@pyconcz", icon: "mastodon" },
  {
    label: "Facebook",
    shortLabel: "Facebook",
    href: "https://www.facebook.com/events/1363197064240927",
    icon: "facebook",
  },
  { label: "YouTube", shortLabel: "YouTube", href: "https://www.youtube.com/@PyConCZ", icon: "youtube" },
  { label: "GitHub", shortLabel: "GitHub", href: "https://github.com/pyvec/cz.pycon.org", icon: "github" },
] as const;

/** Socials shown as icons in "Follow us on" blocks (GitHub is footer/menu only). */
export const followLinks = socialLinks.filter((item) => item.icon !== "github");

export const pastEditions = [2015, 2016, 2017, 2018, 2019, 2020, 2023];

interface FooterGroup {
  label: string;
  links: { label: string; href: string }[];
}

/** Footer link columns; groups without links are not rendered. */
export const footerGroups: FooterGroup[] = [
  { label: "Event", links: [{ label: "Volunteer", href: `${baseUrl}volunteer/` }] },
  { label: "Program", links: [] },
  {
    label: "About",
    links: [
      { label: "Sponsorship", href: `${baseUrl}sponsorship/` },
      { label: "Code of Conduct", href: `${baseUrl}coc/` },
    ],
  },
];

export function isCurrentPage(href: string, pathname: string): boolean {
  return pathname === href || pathname === href.replace(/\/$/, "");
}
