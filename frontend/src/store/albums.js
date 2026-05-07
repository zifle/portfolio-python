import {defineStore} from "pinia";
import {ref} from "vue";

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
                data.map(item => {item.details = false; return item;});
                albums.value = data;
                resolve(data);
            }
        })
        return getAlbumsPromise;
    }

    async function getAlbum(slug) {
        await getAlbumsPromise;
        let albumIdx = -1;
        if (albums.value.length > 0) {
            albumIdx = albums.value.findIndex(a => a.slug === slug);
            if (albumIdx >= 0) {
                const album = albums.value[albumIdx];
                if (album.details) {
                    return album;
                }
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
            album.details = true;
            if (albumIdx >= 0) {
                albums.value[albumIdx] = album;
            } else {
                albums.value.push(album);
            }
            return album;
        }
    }

    return {
        albums,
        getAlbums,
        getAlbum
    }
});