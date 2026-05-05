import {createRouter, createWebHistory} from "vue-router";
import {useAuthStore} from "../store/auth";

const routes = [
    {
        path: '/',
        name: 'home',
        component: () => import('../pages/home.vue')
    },
    {
        path: '/albums/{slug}',
        name: 'album',
        component: () => import('../pages/album.vue')
    },
    {
        path: '/login',
        name: 'login',
        component: () => import('../pages/login.vue')
    },
    {
        path: '/admin',
        name: 'admin',
        component: () => import('../pages/admin.vue'),
        meta: {
            requiresAuth: true
        },
        children: [
            {
                path: 'categories',
                name: 'admin-categories',
                component: () => import('../pages/admin/categories/list.vue')
            },
            {
                path: 'locations',
                name: 'admin-locations',
                component: () => import('../pages/admin/locations/list.vue')
            },
            {
                path: 'albums',
                name: 'admin-album-list',
                component: () => import('../pages/admin/albums/list.vue')
            },
            {
                path: 'albums/create',
                name: 'admin-album-create',
                component: () => import('../pages/admin/albums/edit.vue')
            },
            {
                path: 'albums/:id(\\d+)/edit',
                name: 'admin-album-edit',
                component: () => import('../pages/admin/albums/edit.vue')
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach((to, from) => {
    const authStore = useAuthStore();

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        return { name: 'login' };
    }
})

export default router