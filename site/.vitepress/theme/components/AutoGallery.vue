<script setup>
import { ref } from 'vue'

const props = defineProps({
  loaders: { type: Array, required: true },
})

const currentIndex = ref(0)
const loaded = ref({})
const loading = ref(false)
const total = ref(props.loaders.length)

async function loadAt(index) {
  if (loaded.value[index]) return loaded.value[index]
  loading.value = true
  try {
    const mod = await props.loaders[index]()
    const url = mod.default
    loaded.value[index] = url
    return url
  } finally {
    loading.value = false
  }
}

function goTo(index) {
  if (index < 0 || index >= total.value) return
  currentIndex.value = index
  loadAt(index)
  // preload neighbors
  loadAt((index + 1) % total.value)
  if (index > 0) loadAt(index - 1)
}

function prev() { goTo((currentIndex.value - 1 + total.value) % total.value) }
function next() { goTo((currentIndex.value + 1) % total.value) }

// Load first image on mount (if any)
if (total.value > 0) loadAt(0)
</script>

<template>
  <div class="auto-gallery">
    <div v-if="total === 0" class="gallery-empty">暂无图片</div>
    <template v-else>
      <div class="gallery-viewer" @click="next">
        <div v-if="loading && !loaded[currentIndex]" class="gallery-loading">加载中...</div>
        <img
          v-if="loaded[currentIndex]"
          :src="loaded[currentIndex]"
          :key="currentIndex"
          class="gallery-image"
          loading="lazy"
        />
      </div>

      <div class="gallery-controls">
        <button class="gallery-btn" @click.stop="prev" :disabled="total <= 1">&lsaquo; 上一张</button>
        <span class="gallery-counter">{{ currentIndex + 1 }} / {{ total }}</span>
        <button class="gallery-btn" @click.stop="next" :disabled="total <= 1">下一张 &rsaquo;</button>
      </div>
    </template>
  </div>
</template>

<style>
.auto-gallery {
  margin: 16px 0;
}

.gallery-viewer {
  position: relative;
  width: 100%;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
}

.gallery-image {
  width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 8px;
}

.gallery-empty,
.gallery-loading {
  color: var(--vp-c-text-2);
  font-size: 14px;
  padding: 40px;
}

.gallery-empty {
  text-align: center;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
}

.gallery-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 12px;
}

.gallery-btn {
  padding: 6px 20px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  cursor: pointer;
  font-size: 14px;
  transition: background 0.15s;
}

.gallery-btn:hover:not(:disabled) {
  background: var(--vp-c-brand-1);
  color: #fff;
  border-color: var(--vp-c-brand-1);
}

.gallery-btn:disabled {
  opacity: 0.4;
  cursor: default;
}

.gallery-counter {
  font-size: 13px;
  color: var(--vp-c-text-2);
  min-width: 60px;
  text-align: center;
}

@media (max-width: 640px) {
  .gallery-viewer {
    min-height: 200px;
  }
  .gallery-btn {
    padding: 4px 12px;
    font-size: 13px;
  }
}
</style>
