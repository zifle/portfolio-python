<script setup>
import {onBeforeRouteUpdate, useRoute} from "vue-router";
import {computed, onMounted, ref, useTemplateRef} from "vue";
import {useAlbumStore} from "../store/albums.js";
import AlbumItems from "../components/albumItems.vue";
import AlbumDescription from "../components/albumDescription.vue";

const route = useRoute();
const albumStore = useAlbumStore();

const album = ref(null)
function loadAlbum(slug) {
    startLoading();
    albumStore.getAlbum(slug)
        .then(a => {
            album.value = a;
        });
}
onMounted(() => {
    loadAlbum(route.params.slug);
});

onBeforeRouteUpdate((to, from) => {
    loadAlbum(to.params.slug);
});

const loading = ref(false);
function startLoading() {
    loadSpinner.value.classList.remove('opacity-0');
    loadSpinner.value.classList.remove('d-none');
    loading.value = true;
}
function stopLoading() {
    loadSpinner.value.classList.add('opacity-0');
    setTimeout(() => {
        loadSpinner.value.classList.add('d-none');
    }, 300);
    loading.value = false;
}

const loadSpinner = useTemplateRef('load-spinner');

const album_items = computed(() => {
    if (album.value && album.value.items) {
        return album.value.items;
    }
    return [];
})
</script>

<template>
    <album-description :loading="loading" :album="album"></album-description>
    <album-items :loading="loading" :items="album_items"
                 @img-loaded="stopLoading"></album-items>
    <div class="d-flex position-fixed justify-content-center loading-spinner" ref="load-spinner">
        <div class="spinner-border"></div>
    </div>
</template>

<style>

.loading-spinner {
    width: 100vw;
    left: 0;
    top: 25vh;
}
</style>