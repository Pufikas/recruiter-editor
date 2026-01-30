<template>
    <div class="overlay" @click.self="emit('close')">
        <div class="card">
            <button class="close" @click="emit('close')">x</button>

            <h2>{{ recruiter.name }}</h2>

            <div v-if="data">
                <p><strong>ID:</strong> {{ data.id }}</p>
                <p><strong>Updated:</strong> {{ data.updated_at.split("T")[0] }}</p>
                <p><strong>Recruited by:</strong> {{ data.recruiter?.name ?? 'not found!' }}</p>
            </div>

            <div v-else>
                Fetching...
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref, watch, defineProps } from 'vue';
const selectedNode = ref(null);
const recruiterData = ref(null);

const props = defineProps({
    recruiter: Object,
    data: Object
});

const emit = defineEmits(['close']);


watch(selectedNode, async (node) => {
    if (!node) return;
    recruiterData.value = await getRecruiterData(node.id);
});

</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.card {
  background: #111;
  color: white;
  padding: 20px;
  border-radius: 12px;
  min-width: 280px;
  max-width: 400px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}

.close {
  float: right;
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
}
</style>