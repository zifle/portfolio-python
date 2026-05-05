import {ref} from "vue";
import {defineStore} from "pinia";
import {getCSRFToken, useAuthStore} from "./auth.js";

export const useLocationStore = defineStore('admin/locations', () => {
    const locations = ref([]);

    async function getLocations(force = false) {
        if (!force && locations.value.length > 0) {
            return locations.value;
        }
        const response = await fetch('/api/locations', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            }
        });

        const locs = await response.json();
        locations.value = locs;
        return locs;
    }

    async function saveLocation(location) {
        const authStore = useAuthStore();
        if (authStore.isAuthenticated) {
            const response = await fetch(`/api/locations`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify(location),
            });
            if (response.ok) {
                await getLocations(true);
            }
        }
    }

    async function deleteLocation(id) {
        const authStore = useAuthStore();
        if (authStore.isAuthenticated) {
            const response = await fetch(`/api/locations/${id}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                }
            });
            if (response.ok) {
                await getLocations(true);
            }
        }
    }

    return {
        locations,
        getLocations,
        saveLocation,
        deleteLocation
    }
})