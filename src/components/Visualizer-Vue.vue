<template>
  <div class="visualizer">
    <h2>3D Product Arrangement Visualization</h2>
    <div v-if="vehicleData">
      <p><strong>Vehicle Length:</strong> {{ vehicleData.length }}</p>
      <p><strong>Vehicle Breadth:</strong> {{ vehicleData.breadth }}</p>
      <p><strong>Vehicle Height:</strong> {{ vehicleData.height }}</p>
      <div ref="threeCanvas" class="three-canvas"></div>
      <div ref="tooltip" class="tooltip">Tooltip</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import * as THREE from 'three'
import axios from 'axios'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

const threeCanvas = ref(null)
const tooltip = ref(null)
const vehicleData = ref(null)
const route = useRoute()

onMounted(async () => {
  const query = route.query
  if (!(query.length && query.breadth && query.height)) return

  vehicleData.value = {
    length: parseFloat(query.length),
    breadth: parseFloat(query.breadth),
    height: parseFloat(query.height),
  }

  await nextTick()

  const canvas = threeCanvas.value
  const width = canvas.clientWidth
  const height = canvas.clientHeight

  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
  camera.position.set(0, 0, Math.max(vehicleData.value.length, vehicleData.value.breadth, vehicleData.value.height) * 2)

  const renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(width, height)
  canvas.appendChild(renderer.domElement)

  const controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05

  const light = new THREE.AmbientLight(0xffffff, 1)
  scene.add(light)

  const vehicleGeometry = new THREE.BoxGeometry(vehicleData.value.length, vehicleData.value.height, vehicleData.value.breadth)
  const vehicleMaterial = new THREE.MeshBasicMaterial({ color: 0x888888, wireframe: true })
  const vehicleBox = new THREE.Mesh(vehicleGeometry, vehicleMaterial)
  vehicleBox.position.set(vehicleData.value.length / 2, vehicleData.value.height / 2, vehicleData.value.breadth / 2)
  scene.add(vehicleBox)

  const { data } = await axios.post('http://localhost:8000/pack', vehicleData.value)
  const packedItems = data.packed_items

  const productBoxes = []

  packedItems.forEach(item => {
    const { length, breadth, height } = item.adjusted_size
    const { x, y, z } = item.position
    const fragility = item.fragility_index

    const geometry = new THREE.BoxGeometry(length, height, breadth)
    const color = getColorByFragility(fragility)
    const material = new THREE.MeshStandardMaterial({ color })
    const box = new THREE.Mesh(geometry, material)

    box.position.set(x + length / 2, z + height / 2, y + breadth / 2)
    box.userData = {
      name: item.product_name,
      id: item.product_id
    }

    scene.add(box)
    productBoxes.push(box)
  })

  const raycaster = new THREE.Raycaster()
  const mouse = new THREE.Vector2()

  renderer.domElement.addEventListener('mousemove', event => {
    const rect = renderer.domElement.getBoundingClientRect()
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

    raycaster.setFromCamera(mouse, camera)
    const intersects = raycaster.intersectObjects(productBoxes)

    if (intersects.length > 0) {
      const object = intersects[0].object
      tooltip.value.style.display = 'block'
      tooltip.value.innerHTML = `🧱 ${object.userData.name} (ID: ${object.userData.id})`
      tooltip.value.style.left = `${event.clientX + 10}px`
      tooltip.value.style.top = `${event.clientY + 10}px`
    } else {
      tooltip.value.style.display = 'none'
    }
  })

  function animate() {
    requestAnimationFrame(animate)
    controls.update()
    renderer.render(scene, camera)
  }

  function getColorByFragility(index) {
    if (index >= 8) return 0xff0000
    if (index >= 5) return 0xffa500
    return 0x00ff00
  }

  animate()
})
</script>

<style scoped>
.visualizer {
  padding: 20px;
  font-family: Arial, sans-serif;
}

.three-canvas {
  width: 100%;
  height: 500px;
  position: relative;
  background-color: #ffffff;
  margin-top: 20px;
}

.tooltip {
  position: absolute;
  display: none;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 5px 8px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  z-index: 10;
}
</style>
