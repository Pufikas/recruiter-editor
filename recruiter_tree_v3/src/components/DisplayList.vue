<template>
  <div>
    <div class="container-wrapper">
      <table>
        <thead>
          <tr>
            <th @click="sortById">ID
              <span>
                {{ sortAsc ? '↑' : '↓' }}
              </span>
            </th>
            <th>NAME</th>
            <th>RECRUITED BY</th>
            <th>UPDATE</th>
          </tr>
        </thead>
       
        <tbody>
          <tr v-for="rec in sortedRecruiters" :key="rec.id">
            <td>{{ rec.id }}</td>
            <td>{{ rec.name }}</td>
            <td>{{ rec.recruiter?.name }}</td>
            <td>{{ new Date(rec.updated_at).toLocaleString() }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watchEffect, watch } from 'vue'
import { supabase } from '../lib/supabaseClient'

const sortAsc = ref(true);
const recruiters = ref([]);
const sortedRecruiters = computed(() => {
  return [...recruiters.value].sort((a, b) =>
    sortAsc.value ? a.id - b.id : b.id - a.id
  )
})

const getRecruiters = async () => {
  const { data } = await supabase
  .from('members')
  .select(`
    id,
    name,
    updated_at,
    recruited_by,
    recruiter:recruited_by(name)`
  ).order('id', { ascending: true })

  recruiters.value = data
}

const sortById = () => {
  sortAsc.value = !sortAsc.value
}

onMounted(() => {
  getRecruiters()
})
</script>

<style scoped>
table, th, td {
  border: 1px solid rgb(255, 255, 255);
}

table {
  margin: 0 auto;
}
</style>
