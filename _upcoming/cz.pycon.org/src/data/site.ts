const baseUrl = import.meta.env.BASE_URL;

interface MenuItem {
  label: string;
  href: string;
  /** Used where the full label doesn't fit: the mobile top bar and the hero tabs below xxl */
  shortLabel?: string;
}

export const menuItems: MenuItem[] = [
  { label: "Home", href: baseUrl },
  { label: "Sponsorship", href: `${baseUrl}sponsorship/` },
  { label: "Call for Proposals", shortLabel: "CFP", href: `${baseUrl}cfp/` },
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
  { label: "LinkedIn", shortLabel: "LinkedIn", href: "https://www.linkedin.com/company/pycon-cz/", icon: "linkedin" },
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
  {
    label: "Program",
    links: [
      { label: "Call for Proposals", href: `${baseUrl}cfp/` },
      { label: "Proposal Guide", href: `${baseUrl}cfp/guide/` },
    ],
  },
  {
    label: "About",
    links: [
      { label: "Sponsorship", href: `${baseUrl}sponsorship/` },
      { label: "Code of Conduct", href: `${baseUrl}coc/` },
      { label: "Privacy Policy", href: `${baseUrl}privacy-policy/` },
    ],
  },
];

export function isCurrentPage(href: string, pathname: string): boolean {
  return pathname === href || pathname === href.replace(/\/$/, "");
}
