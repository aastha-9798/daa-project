import { createRouter, createWebHistory } from 'vue-router'
import VehicleInput from '../components/VehicleInput.vue'
import ProductVisualizer from '../components/Visualizer-Vue.vue';

const routes = [
  { path: '/', component: VehicleInput },
  {
    path: '/visualizer',
    name: 'ProductVisualizer',
    component: ProductVisualizer
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
