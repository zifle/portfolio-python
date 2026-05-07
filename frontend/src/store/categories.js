import {ref} from "vue";
import {defineStore} from "pinia";
import {getCSRFToken, useAuthStore} from "./auth.js";

export const useCategoryStore = defineStore('categories', () => {
    const categories = ref([]);

    async function getCategories(force = false) {
        if (!force && categories.value.length > 0) {
            return categories.value;
        }
        const response = await fetch('/api/categories', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
            }
        });

        const cats = await response.json();
        categories.value = cats;
        return cats;
    }

    async function saveCategory(category) {
        const authStore = useAuthStore();
        if (authStore.isAuthenticated) {
            const response = await fetch(`/api/categories`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify(category),
            });
            if (response.ok) {
                await getCategories(true);
            }
        }
    }

    async function deleteCategory(id) {
        const authStore = useAuthStore();
        if (authStore.isAuthenticated) {
            const response = await fetch(`/api/categories/${id}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                }
            });
            if (response.ok) {
                await getCategories(true);
            }
        }
    }

    return {
        categories,
        getCategories,
        saveCategory,
        deleteCategory,
    }
})