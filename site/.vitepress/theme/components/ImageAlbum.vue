<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  images: { type: Array, required: true },
})

const currentIndex = ref(0)
const showLightbox = ref(false)

const currentImage = computed(() => props.images[currentIndex.value])

function open(index) {
  currentIndex.value = index
  showLightbox.value = true
}

function close() {
  showLightbox.value = false
}

function prev() {
  currentIndex.value = (currentIndex.value - 1 + props.images.length) % props.images.length
}

function next() {
  currentIndex.value = (currentIndex.value + 1) % props.images.length
}

function onKeydown(e) {
  if (!showLightbox.value) return
  if (e.key === 'Escape') close()
  if (e.key === 'ArrowLeft') prev()
  if (e.key === 'ArrowRight') next()
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <div class="album-grid">
    <div
      v-for="(img, idx) in images"
      :key="img"
      class="album-thumb"
      @click="open(idx)"
    >
      <img :src="img" loading="lazy" />
    </div>
  </div>

  <Teleport to="body">
    <div v-if="showLightbox" class="lightbox-overlay" @click.self="close">
      <button class="lightbox-close" @click="close">&times;</button>
      <button class="lightbox-nav lightbox-prev" @click.stop="prev">&lsaquo;</button>
      <div class="lightbox-content">
        <img :src="currentImage" />
        <div class="lightbox-counter">{{ currentIndex + 1 }} / {{ images.length }}</div>
      </div>
      <button class="lightbox-nav lightbox-next" @click.stop="next">&rsaquo;</button>
    </div>
  </Teleport>
</template>

<style>
.album-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 8px;
  margin: 16px 0;
}

.album-thumb {
  aspect-ratio: 4 / 3;
  overflow: hidden;
  border-radius: 6px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.15s;
}

.album-thumb:hover {
  border-color: var(--vp-c-brand-1);
}

.album-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.lightbox-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
}

.lightbox-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 90vw;
  max-height: 90vh;
}

.lightbox-content img {
  max-width: 90vw;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 4px;
}

.lightbox-counter {
  color: #ccc;
  margin-top: 12px;
  font-size: 14px;
}

.lightbox-close {
  position: absolute;
  top: 16px;
  right: 24px;
  background: none;
  border: none;
  color: #fff;
  font-size: 40px;
  cursor: pointer;
  line-height: 1;
}

.lightbox-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.1);
  border: none;
  color: #fff;
  font-size: 48px;
  padding: 0 16px;
  cursor: pointer;
  border-radius: 4px;
  line-height: 1.4;
}

.lightbox-nav:hover {
  background: rgba(255,255,255,0.25);
}

.lightbox-prev { left: 16px; }
.lightbox-next { right: 16px; }

@media (max-width: 640px) {
  .album-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 4px;
  }
  .lightbox-nav {
    font-size: 36px;
    padding: 0 8px;
  }
}
</style>
