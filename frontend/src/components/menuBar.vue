<script setup>
import {useAuthStore} from "../store/auth.js";
import {computed, onMounted, ref, watch} from "vue";
import 'bootstrap/js/src/collapse.js';
import 'bootstrap/js/src/dropdown.js';
import router from "../router/index.js";
import {useCategoryStore} from "../store/categories.js";
import {useAlbumStore} from "../store/albums.js";

const authStore = useAuthStore();
const isAdmin = computed(() => {
    return authStore.isAuthenticated;
});

const albumStore = useAlbumStore();
const catStore = useCategoryStore();

onMounted(() => {
    catStore.getCategories();
    albumStore.getAlbums();
});

const catMenu = ref([]);
const rootAlbums = ref([]);
function buildCategories(cats, albums) {
    const oCats = {}
    const catMenuMap = []
    for (const cat of cats) {
        oCats[cat.id] = {
            id: cat.id,
            name: cat.name,
            order: cat.order,
            albums: []
        };
        catMenuMap.push(oCats[cat.id]);
    }

    const rootAlbumMap = albums.filter(a => !a.category);
    catMenuMap.sort((a, b) => a.order - b.order);
    for (const album of albums) {
        if (album.category && oCats.hasOwnProperty(album.category)) {
            oCats[album.category].albums.push(album);
        }
    }

    catMenu.value = catMenuMap.filter(cat => cat.albums.length > 0);
    rootAlbums.value = rootAlbumMap;
}

watch(() => {
    buildCategories(catStore.categories, albumStore.albums);
});
</script>

<template>
    <nav class="navbar navbar-expand-lg">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">Niels Pedersen Photography</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <router-link :to="{name: 'home'}" class="nav-link" active-class="active">Home</router-link>
                    </li>

                    <li v-for="cat of catMenu" class="nav-item dropdown">
                        <a href="#" class="nav-link dropdown-toggle" role="button" data-bs-toggle="dropdown"
                           aria-expanded="false">{{ cat.name }}</a>
                        <ul class="dropdown-menu">
                            <li v-for="album of cat.albums">
                                <router-link :to="{name: 'album', params: {slug: album.slug}}" class="dropdown-item">
                                    {{ album.title }}
                                </router-link>
                            </li>
                        </ul>
                    </li>

                    <li v-for="album of rootAlbums" class="nav-item">
                        <router-link :to="{name: 'album', params: {slug: album.slug}}" class="nav-link" active-class="active">
                            {{ album.title }}
                        </router-link>
                    </li>
                </ul>

                <ul v-if="isAdmin" class="navbar-nav mb-2 mb-lg-0 d-flex justify-content-lg-end">
                    <li class="nav-item">
                        <router-link :to="{name: 'admin'}" class="nav-link" active-class="active">Admin</router-link>
                    </li>
                    <li class="nav-item">
                        <span class="nav-link clickable" @click="authStore.logout(router)" aria-label="Logout">
                            <span class="d-lg-none">Logout</span>
                            ➜]
                        </span>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
</template>

<style scoped>

</style>