import {createRouter, createWebHistory} from "vue-router";
import {useAuthStore} from "../store/auth";

const routes = [
    {
        path: '/',
        name: 'home',
        component: () => import('@/pages/home.vue')
    },
    {
        path: '/album/{slug}',
        name: 'album',
        component: () => import('@/pages/album.vue')
    },
    {
        path: '/login',
        name: 'login',
        component: () => import('@/pages/login.vue')
    },
    {
        path: '/admin',
        name: 'admin',
        component: () => import('@/pages/admin.vue'),
        meta: {
            requiresAuth: true
        }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach((to, from) => {
    const authStore = useAuthStore();

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        debugger;
        return { name: 'login' };
    }
})

export default router