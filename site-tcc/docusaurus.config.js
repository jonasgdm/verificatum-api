// @ts-check
import { themes as prismThemes } from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Implementação Criptográfica para Mobilidade Segura em Eleições Brasileiras',
  tagline: 'TCC 2025 – Luis Dellano',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://luisdellano.github.io',
  baseUrl: '/verificatum-api/',

  organizationName: 'luisdellano',
  projectName: 'verificatum-api',

  trailingSlash: false,
  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'pt-BR',
    locales: ['pt-BR'],
  },

  presets: [
    [
      'classic',
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: undefined,    // tira "edit this page"
        },
        blog: false,              // remove blog completamente
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig: {
    image: 'img/social-card.jpg',
    colorMode: {
      respectPrefersColorScheme: true,
    },

    navbar: {
      title: 'Verificatum API – TCC',
      logo: {
        alt: 'Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          label: 'Documentação',
          position: 'left',
        },
        {
          href: 'https://github.com/luisdellano/verificatum-api',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },

    footer: {
      style: 'dark',
      links: [],
      copyright: `TCC – Mobilidade Segura em Eleições · ${new Date().getFullYear()}`,
    },

    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  },
};

export default config;
