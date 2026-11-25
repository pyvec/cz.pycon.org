import type { ImageMetadata } from "astro";
import epsLogo from "../assets/sponsors/europython-society.svg";
import psfLogo from "../assets/sponsors/python-software-foundation.svg";

export interface Sponsor {
  name: string;
  url: string;
  /** Logos come from the sponsor's official brand page, at most optimized with svgo */
  logo: ImageMetadata;
  /** Paragraphs of trusted HTML, rendered with set:html */
  description: string[];
}

export interface SponsorTier {
  /** Anchor on the sponsors page */
  id: string;
  label: string;
  sponsors: Sponsor[];
}

export const sponsorTiers: SponsorTier[] = [
  {
    id: "community-gold",
    label: "Community Gold Partners",
    // Alphabetical within a tier
    sponsors: [
      {
        name: "EuroPython Society",
        url: "https://www.europython-society.org/",
        logo: epsLogo,
        description: [
          'The EuroPython Society (EPS) is a&nbsp;Swedish non-profit organization which organizes <a href="https://www.europython.eu/">EuroPython</a> conferences and supports the&nbsp;Python community in Europe.',
          'The&nbsp;EPS was formed in 2004, with the&nbsp;mission to turn EuroPython into a&nbsp;successful <a href="https://www.python.org/">Python</a> conference series for the&nbsp;years to come. In 2016, the&nbsp;EPS extended its <a href="https://www.europython-society.org/mission/">mission</a> to further the&nbsp;use of the&nbsp;programming language Python in Europe and organize events centered around Python to support this.',
        ],
      },
      {
        name: "Python Software Foundation",
        url: "https://www.python.org/psf-landing/",
        logo: psfLogo,
        description: [
          "The mission of the&nbsp;Python Software Foundation is to promote, protect, and advance the&nbsp;Python programming language, and to support and facilitate the&nbsp;growth of a&nbsp;diverse and international community of Python programmers. The&nbsp;majority of the&nbsp;PSF’s work is focused on empowering and supporting people within the&nbsp;Python community.",
          "The&nbsp;PSF has active grant programs that support sprints, conferences, meetups, user groups, and Python development efforts all over the&nbsp;world. In addition, the&nbsp;PSF underwrites and runs PyCon&nbsp;US, the&nbsp;primary Python community conference. Being part of the&nbsp;PSF means being part of the&nbsp;Python community. Recently we changed the&nbsp;PSF to an open membership organization, so that everyone who uses and supports Python can join.",
          'To learn more, visit the&nbsp;<a href="https://www.python.org/psf/membership/">PSF’s page about membership</a>.',
        ],
      },
    ],
  },
];
