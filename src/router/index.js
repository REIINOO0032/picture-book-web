import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Profile from '../views/Profile.vue'
import Search from '../views/Search.vue'
import Creation from '../views/Creation.vue'
import BookRead from '../views/BookRead.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/profile', name: 'Profile', component: Profile },
  { path: '/search', name: 'Search', component: Search },
  { path: '/creation', name: 'Creation', component: Creation },
  { path: '/read/:id', name: 'BookRead', component: BookRead }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router