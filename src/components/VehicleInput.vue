<template>
  <div class="vehicle-input">
    <h2>Enter Vehicle Dimensions</h2>
    <form @submit.prevent="submitVehicleDimensions">
      <label for="vehicleLength">Length:</label>
      <input type="number" v-model="vehicleLength" required />

      <label for="vehicleBreadth">Breadth:</label>
      <input type="number" v-model="vehicleBreadth" required />

      <label for="vehicleHeight">Height:</label>
      <input type="number" v-model="vehicleHeight" required />

      <button type="submit">Submit</button>
    </form>
     <div class="visualize-button-container">
         <button class="visualize-button" @click="goToVisualization">Visualize</button>
     </div>
    <p v-if="message" :class="{ success: isSuccess, error: !isSuccess }">
      {{ message }}
    </p>
  </div>
 
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      vehicleLength: null,
      vehicleBreadth: null,
      vehicleHeight: null,
      message: '',
      isSuccess: false
    };
  },
  methods: {
    async submitVehicleDimensions() {
      try {
        const payload = {
          length: this.vehicleLength,
          breadth: this.vehicleBreadth,
          height: this.vehicleHeight,
        };

        const response = await axios.post('http://127.0.0.1:8000/vehicle', payload);

        if (response.status === 200) {
          this.message = 'Vehicle dimensions successfully submitted.';
          this.isSuccess = true;
        } else {
          this.message = 'Something went wrong. Please try again.';
          this.isSuccess = false;
        }
      } catch (error) {
        console.error(error);
        this.message = 'Failed to connect to backend.';
        this.isSuccess = false;
      }
    },
    goToVisualization() {
      this.$router.push({
        name: 'ProductVisualizer',
        query: {
          length: this.vehicleLength,
          breadth: this.vehicleBreadth,
          height: this.vehicleHeight
        }
      });
    }
  }
};
</script>

<style scoped>
.vehicle-input {
  max-width: 400px;
  margin: auto;
  padding: 1.5rem;
  border: 1px solid #ccc;
  border-radius: 12px;
  box-shadow: 2px 2px 12px #eee;
}

h2 {
  font-size: 1.2em;
  margin-bottom: 10px;
  text-align: left;
}

label {
  display: block;
  margin: 8px 0 4px;
  font-size: 0.9em;
}

input {
  padding: 6px;
  width: 100%;
  margin-bottom: 12px;
  border-radius: 4px;
  border: 1px solid #ffffff;
}

button {
  padding: 8px 12px;
  background-color: #163e7a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
}

button:hover {
  background-color: #1b3c61;
}

p.success {
  color: green;
  margin-top: 10px;
}

p.error {
  color: red;
  margin-top: 10px;
}
.visualize-button-container {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.visualize-button {
  padding: 10px 20px;
  background-color: #0c6c3e;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.visualize-button:hover {
  background-color: #095b34;
}
</style>
