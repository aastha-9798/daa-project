<template>
  <div class="visualizer">
    <h2>3D Product Arrangement Visualization</h2>
    <div v-if="vehicleData">
      <p><strong>Vehicle Length:</strong> {{ vehicleData.length }}</p>
      <p><strong>Vehicle Breadth:</strong> {{ vehicleData.breadth }}</p>
      <p><strong>Vehicle Height:</strong> {{ vehicleData.height }}</p>

      <div
        ref="threeCanvas"
        class="three-canvas"
        style="width: 100%; height: 500px; position: relative;"
      ></div>

      <div
        class="tooltip"
        :style="{
          top: tooltip.y + 'px',
          left: tooltip.x + 'px',
          display: tooltip.visible ? 'block' : 'none'
        }"
      >
        <p><strong>ID:</strong> {{ tooltip.id }}</p>
        <p><strong>Name:</strong> {{ tooltip.name }}</p>
      </div>

      <!-- Final Report Button -->
      <div class="final-report-btn">
        <button @click="goToReport">Final Report</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as THREE from 'three'
import axios from 'axios'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

const threeCanvas = ref(null)
const tooltip = ref({ visible: false, x: 0, y: 0, id: '', name: '' })
const vehicleData = ref(null)
const packedItems = ref([])
const route = useRoute()
const router = useRouter()

onMounted(async () => {
  const query = route.query
  if (!(query.length && query.breadth && query.height)) return

  vehicleData.value = {
    length: parseFloat(query.length),
    breadth: parseFloat(query.breadth),
    height: parseFloat(query.height),
  }

  await nextTick()

  const canvasEl = threeCanvas.value
  const width = canvasEl.clientWidth
  const height = canvasEl.clientHeight

  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
  camera.position.set(
    vehicleData.value.length,
    vehicleData.value.height,
    vehicleData.value.breadth * 2
  )

  const renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(width, height)
  canvasEl.appendChild(renderer.domElement)

  const controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true

  const light = new THREE.AmbientLight(0xffffff, 1)
  scene.add(light)

  const raycaster = new THREE.Raycaster()
  const mouse = new THREE.Vector2()

  const vehicleBox = new THREE.Mesh(
    new THREE.BoxGeometry(
      vehicleData.value.length,
      vehicleData.value.height,
      vehicleData.value.breadth
    ),
    new THREE.MeshBasicMaterial({ color: 0x888888, wireframe: true })
  )
  vehicleBox.position.set(
    vehicleData.value.length / 2,
    vehicleData.value.height / 2,
    vehicleData.value.breadth / 2
  )
  scene.add(vehicleBox)

  const { data } = await axios.post('http://localhost:8000/pack', vehicleData.value)
  packedItems.value = data.packed_items

  const boxes = []

  packedItems.value.forEach(item => {
    const { length, breadth, height } = item.adjusted_size
    const { x, y, z } = item.position

    const geometry = new THREE.BoxGeometry(length, height, breadth)
    const material = new THREE.MeshStandardMaterial({ color: getColor(item.fragility_index) })
    const mesh = new THREE.Mesh(geometry, material)

    mesh.position.set(
      x + length / 2,
      z + height / 2,
      y + breadth / 2
    )

    mesh.userData = {
      id: item.product_id,
      name: item.product_name,
    }

    scene.add(mesh)
    boxes.push(mesh)

    const edges = new THREE.EdgesGeometry(geometry)
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0x000000 })
    const wireframe = new THREE.LineSegments(edges, lineMaterial)
    wireframe.position.copy(mesh.position)
    scene.add(wireframe)
  })

  function getColor(index) {
    if (index >= 8) return 0xff0000
    if (index >= 5) return 0xffa500
    return 0x00ff00
  }

  canvasEl.addEventListener('mousemove', (event) => {
    const rect = canvasEl.getBoundingClientRect()
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

    raycaster.setFromCamera(mouse, camera)
    const intersects = raycaster.intersectObjects(boxes)

    if (intersects.length > 0) {
      const { id, name } = intersects[0].object.userData
      tooltip.value = {
        visible: true,
        x: event.clientX - rect.left + 10,
        y: event.clientY - rect.top + 10,
        id,
        name
      }
    } else {
      tooltip.value.visible = false
    }
  })

  const animate = () => {
    requestAnimationFrame(animate)
    controls.update()
    renderer.render(scene, camera)
  }

  animate()
})

function goToReport() {
  const reportData = packedItems.value.map(item => ({
    id: item.product_id,
    name: item.product_name,
    dimensions: item.adjusted_size,
    distance: item.distance,
    coordinates: item.position
  }))

  const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
  const fileUrl = URL.createObjectURL(blob)

  // Save to session storage
  sessionStorage.setItem('reportFile', fileUrl)

  // Optionally download file
  // const a = document.createElement('a')
  // a.href = fileUrl
  // a.download = 'final_report.json'
  // a.click()

  // Navigate to report
  router.push({
    name: 'FinalReport',
  })
}
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
}

.tooltip {
  position: absolute;
  background-color: rgba(0, 0, 0, 0.8);
  color: #fff;
  padding: 6px 10px;
  font-size: 13px;
  border-radius: 4px;
  pointer-events: none;
  z-index: 10;
}

.final-report-btn {
  text-align: center;
  margin-top: 20px;
}

.final-report-btn button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}
</style>
