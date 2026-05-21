import {defineStore} from "pinia";
import {ref} from "vue";
import {getCSRFToken, useAuthStore} from "../auth.js";
import router from "../../router/index.js";

export const useAdminAlbumStore = defineStore('admin/albums', () => {
    const albums = ref([]);

    async function getAlbums(force = false) {
        if (!force && albums.value.length > 0) {
            return albums.value;
        }
        const response = await fetch('/api/albums', {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            }
        });
        if (response.ok) {
            const data = await response.json();
            albums.value = data;
            return data;
        }
        if (response.status === 401) {
            await router.push({name: 'login'});
        }
    }

    async function getAlbum(id) {
        const response = await fetch(`/api/albums/${id}`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            }
        });
        if (response.ok) {
            const obj = await response.json();
            return obj;
        }
    }

    async function saveAlbum(album) {
        const authStore = useAuthStore();
        if (authStore.isAuthenticated) {
            const response = await fetch(`/api/albums`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify(album),
            });
            if (response.ok) {
                const data = await response.json();
                getAlbums(true);
                if (album.id !== data.id) {
                    await router.push({name: 'admin-album-edit', params: {id: data.id}});
                } else {
                    return data;
                }
            }
        }
    }

    async function deleteAlbum(id) {
        const authStore = useAuthStore();
        if (authStore.isAuthenticated) {
            const response = await fetch(`/api/albums/${id}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                }
            });
            if (response.ok) {
                await getAlbums(true);
            }
        }
    }

    async function togglePublished(album) {
        const authStore = useAuthStore();
        if (authStore.isAuthenticated) {
            const response = await fetch(`/api/albums/${album.id}/toggle-publish`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({publish: !album.published}),
            });
            if (response.ok) {
                await getAlbums(true);
            }
        }
    }

    async function uploadImages(formData) {
        const authStore = useAuthStore();
        if (authStore.isAuthenticated) {
            const response = await fetch('/api/upload', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Accept': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: formData,
            });
            return await response.json();
        }
    }

    async function saveTextBox(box) {
        const authStore = useAuthStore();
        if (authStore.isAuthenticated) {
            const response = await fetch('/api/texts', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify(box),
            });
            return await response.json();
        }
    }

    async function saveImageDescription(img) {
        const authStore = useAuthStore();
        if (authStore.isAuthenticated) {
            const response = await fetch(`/api/images/${img.id}/description`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify(img),
            });
        }
    }

    return {
        albums,
        getAlbums,
        getAlbum,
        saveAlbum,
        togglePublished,
        uploadImages,
        deleteAlbum,
        saveTextBox,
        saveImageDescription,
    };
});