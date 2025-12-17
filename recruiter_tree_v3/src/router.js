import { createMemoryHistory, createRouter } from 'vue-router';

import DisplayList from './components/DisplayList.vue'
import Tree from './components/Tree.vue';
import Home from './components/Home.vue';

const routes = [
    { path: '/', component: Home },
    { path: '/tree', component: Tree },
    { path: '/display-list', component: DisplayList }
];

export const router = createRouter({
    history: createMemoryHistory(),
    routes,
});

export default router;