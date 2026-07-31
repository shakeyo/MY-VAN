import { defineConfig } from 'vitepress'

const modulesSidebar = [
  { text: '基础', items: [
    { text: '00 底盘', link: '/modules/00-chassis/' },
  ]},
  { text: '总纲', items: [
    { text: '01 整车布局与结构', link: '/modules/01-vehicle-layout/' },
  ]},
  { text: '外观 / 外部', items: [
    { text: '02 外部扩展', link: '/modules/02-external/' },
    { text: '03 外观装饰', link: '/modules/03-exterior-appearance/' },
  ]},
  { text: '管线系统', items: [
    { text: '04 电力系统', link: '/modules/04-power-system/' },
    { text: '05 用水系统', link: '/modules/05-water-system/' },
    { text: '06 HVAC 系统', link: '/modules/06-hvac/' },
  ]},
  { text: '内饰', items: [
    { text: '07 柜体与台面', link: '/modules/07-cabinetry/' },
    { text: '08 床铺与座椅', link: '/modules/08-bed-and-seat/' },
    { text: '09 淋浴模块', link: '/modules/09-shower-module/' },
  ]},
  { text: '集成', items: [
    { text: '10 智能控制', link: '/modules/10-smart-control/' },
    { text: '11 影音娱乐', link: '/modules/11-entertainment/' },
  ]},
]

export default defineConfig({
  title: 'MY-VAN',
  description: '房车改装文档',
  base: '/MY-VAN/',
  themeConfig: {
    nav: [
      { text: '模块', link: '/modules/' },
      { text: 'GitHub', link: 'https://github.com/shakeyo/MY-VAN' },
    ],
    sidebar: {
      '/modules/': modulesSidebar,
    },
    search: {
      provider: 'local',
    },
    outline: { level: [2, 3] },
  },
  ignoreDeadLinks: true,
  vite: {
    assetsInclude: ['**/*.PNG', '**/*.JPG', '**/*.JPEG'],
  },
})
