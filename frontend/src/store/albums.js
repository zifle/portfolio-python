import {defineStore} from "pinia";
import {ref} from "vue";
import {getCSRFToken} from "./auth.js";

export const useAlbumStore = defineStore('albums', () => {
    const albums = ref([]);

    let getAlbumsPromise = null;
    function getAlbums() {
        if (getAlbumsPromise) {
            return getAlbumsPromise;
        }
        getAlbumsPromise = new Promise(async (resolve, reject) => {
            if (albums.value.length > 0) {
                resolve(albums.value);
                return
            }
            const response = await fetch('/api/albums', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                }
            });
            if (response.ok) {
                const data = await response.json();
                albums.value = data;
                resolve(data);
                return
            }
        })
        return getAlbumsPromise;
    }

    async function getAlbum(slug) {
        await getAlbumsPromise;
        if (albums.value.length > 0) {
            const album = albums.value.find(a => a.slug === slug);
            if (album) {
                return album;
            }
        }
        const response = await fetch(`/api/albums/${slug}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            }
        });
        if (response.ok) {
            const album = await response.json();
            albums.value.push(album);
            return album;
        }
    }

    return {
        albums,
        getAlbums,
        getAlbum
    }
});