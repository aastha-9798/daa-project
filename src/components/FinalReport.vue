<template>
  <div class="final-report">
    <h2>Final Report</h2>

    <div v-if="loading">Loading report data...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="reportData.length === 0">
      No report data found. Please generate the report first.
    </div>
    <table v-else>
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Fragility</th>
          <th>Dimensions (L×B×H)</th>
          <th>Coordinates (X, Y, Z)</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in reportData" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.name }}</td>
          <td>{{item.fragility}}</td>
          <td>{{ formatDimensions(item.dimensions) }}</td>
          <td>{{ formatCoordinates(item.coordinates) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const reportData = ref([])
const loading = ref(true)
const error = ref(null)

function formatDimensions(dim) {
  return `${dim.length} × ${dim.breadth} × ${dim.height}`
}

function formatCoordinates(pos) {
  return `${pos.x}, ${pos.y}, ${pos.z}`
}

onMounted(async () => {
  const fileUrl = sessionStorage.getItem('reportFile')
  if (!fileUrl) {
    error.value = 'No report file found in session storage.'
    loading.value = false
    return
  }

  try {
    const response = await fetch(fileUrl)
    if (!response.ok) throw new Error('Failed to load report file.')

    const json = await response.json()

    // Sort by numeric part of the ID
    json.sort((a, b) => {
      const numA = parseInt(a.id.replace(/\D/g, ''))
      const numB = parseInt(b.id.replace(/\D/g, ''))
      return numA - numB
    })

    reportData.value = json
  } catch (err) {
    error.value = err.message || 'Error loading report data.'
  } finally {
    loading.value = false
  }
})

</script>

<style scoped>
.final-report {
  padding: 20px;
  font-family: Arial, sans-serif;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th,
td {
  padding: 10px;
  border: 1px solid #ccc;
  text-align: center;
}

.error {
  color: red;
  font-weight: bold;
}
</style>
