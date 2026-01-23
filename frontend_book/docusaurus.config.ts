import { themes as prismThemes } from 'prism-react-renderer';
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Connect AI intelligence to humanoid robot control',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  // ✅ REQUIRED FOR VERCEL
  url: 'https://hackathon018-physical-ai-humanoid-textbook-c3j3ywopt.vercel.app/',
  baseUrl: '/',
  trailingSlash: false,

  // ✅ Prevent build from failing due to missing docs
  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/', // Serve docs at root (/)
          sidebarPath: './sidebars.ts',
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',

    colorMode: {
      respectPrefersColorScheme: true,
    },

    navbar: {
      title: 'Humanoid Robotics',
      hideOnScroll: true,
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Course',
        },
        {
          href: 'https://github.com/facebook/docusaurus',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },

    footer: {
      style: 'dark',
      links: [
        {
          title: 'Course',
          items: [
            {
              label: 'Module 1',
              to: '/modules/module-1/intro',
            },
            {
              label: 'Module 2',
              to: '/modules/module-2/gazebo-physics',
            },
            {
              label: 'Module 3',
              to: '/modules/module-3/isaac-sim-overview',
            },
            {
              label: 'Module 4',
              to: '/modules/module-4/intro',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI Course.`,
    },

    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
