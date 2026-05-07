import {ref} from "vue";
import {defineStore} from "pinia";
import {getCSRFToken, useAuthStore} from "./auth.js";

export const useLocationStore = defineStore('admin/locations', () => {
    const locations = ref([]);

    let getLocationsPromise = null;
    async function getLocations(force = false) {
        if (getLocationsPromise) {
            return await getLocationsPromise;
        }
        if (locations.value.length > 0 && !force) {
            return locations.value;
        }

        getLocationsPromise = new Promise(async (resolve, reject) => {
            if (!force && locations.value.length > 0) {
                return locations.value;
            }
            const response = await fetch('/api/locations', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Accept': 'application/json',
                }
            });
            if (response.ok) {
                const locs = await response.json();
                locations.value = locs;
                resolve(locs);
                getLocationsPromise = null;
            }
        });
        return await getLocationsPromise;
    }

    async function getLocation(id) {
        if (getLocationsPromise) {
            await getLocationsPromise;
        }
        if (locations.value.length > 0) {
            const loc = locations.value.find(loc => loc.id === id);
            if (loc) {
                return loc;
            }
        }
        return null;
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
        getLocation,
        saveLocation,
        deleteLocation
    }
})