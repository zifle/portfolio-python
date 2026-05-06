<script setup lang="ts">
import {onMounted, ref} from "vue";
import EditForm from "./editForm.vue";
import {useAdminAlbumStore} from "../../../store/admin/albums";
import {useRoute} from "vue-router";

const route = useRoute();
const albumStore = useAdminAlbumStore();
const album = ref({
    id: 0,
    title: '',
    items: []
});
onMounted(() => {
    const albumId = route.params.id;
    albumStore.getAlbum(albumId).then((data) => {
        album.value = data;
    })
});

function setAlbumItems(items) {
    album.value.items = items;
}
</script>

<template>
    <edit-form :album="album" @album-saved="(na) => album = na"
                @album-items="(itms) => setAlbumItems(itms)"></edit-form>
</template>

<style scoped>

</style>