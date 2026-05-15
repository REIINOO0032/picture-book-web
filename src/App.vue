<template>
  <router-view />
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
const router = useRouter()
const route = useRoute()

const go = (path) => {
  router.push(path)
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app-container {
  width: 100%;
  min-height: 100vh;
  padding-bottom: 70px; /* 给底部导航留位置 */
  position: relative;
}

.main-content {
  width: 100%;
}

/* 底部导航样式 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 70px;
  background: #ffffff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 999;
  border-top-left-radius: 16px;
  border-top-right-radius: 16px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 12px;
  cursor: pointer;
  gap: 4px;
}

.nav-item .icon {
  font-size: 24px;
}

.nav-item.active {
  color: #2d5af1;
  font-weight: bold;
}
</style>