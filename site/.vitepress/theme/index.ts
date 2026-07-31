import DefaultTheme from 'vitepress/theme'
import ImageAlbum from './components/ImageAlbum.vue'
import AutoGallery from './components/AutoGallery.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('ImageAlbum', ImageAlbum)
    app.component('AutoGallery', AutoGallery)
  },
}
