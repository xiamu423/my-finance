import { createRouter, createWebHistory } from 'vue-router'
import SignalList from './views/SignalList.vue'
import SignalDetail from './views/SignalDetail.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: SignalList
    },
    {
      path: '/signal/:id',
      name: 'signal-detail',
      component: SignalDetail
    }
  ]
})

export default router
