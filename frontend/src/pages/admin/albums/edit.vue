<script setup>
import {useRoute} from "vue-router";
import {useAdminAlbumStore} from "../../../store/admin/albums.js";
import {onMounted, ref, useTemplateRef} from "vue";
import {useCategoryStore} from "../../../store/categories.js";
import {useLocationStore} from "../../../store/locations.js";

const route = useRoute();
const albumStore = useAdminAlbumStore();
const catStore = useCategoryStore();
const locStore = useLocationStore();

const album = ref({
    id: 0,
    title: '',
    items: []
});

onMounted(() => {
    let albumId = 0;
    if (route.name.endsWith('create')) {
        album.value = {
            id: 0,
            title: '',
            slug: '',
            location: null,
            category: null,
            description: '',
            date_start: null,
            date_end: null,
            items: []
        }
    } else {
        albumId = route.params.id;
        albumStore.getAlbum(albumId).then((data) => {
            album.value = data;
        })
    }
    catStore.getCategories();
    locStore.getLocations();
});

const fileUpload = useTemplateRef('fileUpload');
const imagePreviews = useTemplateRef('imagePreview');
onMounted(() => {
    fileUpload.value.addEventListener("change", (e) => {
        imagePreviews.value.innerHTML = '';
        const files = e.target.files;
        const data = new FormData();

        let idx = 0;
        for (const file of files) {
            if (!file.type.startsWith("image/")) {
                continue;
            }

            const cont = document.createElement('div');
            const img = document.createElement("img");
            cont.classList.add('col-3', 'mb-2');
            img.classList.add('image-preview');
            img.file = file;
            cont.appendChild(img);
            imagePreviews.value.appendChild(cont);

            const reader = new FileReader();
            reader.onload = e => {
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);

            data.append('file_'+idx, file);
            idx++;
        }

        albumStore.uploadImages(album.value, data).then((data) => {
            console.log(data);
        });
    });
});
</script>

<template>
    <h2>
        <template v-if="album.id">Edit {{ album.title }}</template>
        <template v-else>Create new album</template>
    </h2>
    <form @submit.prevent="albumStore.saveAlbum(album)">
        <div class="mb-3">
            <label for="album-title" class="form-label">Album Title</label>
            <input type="text" id="album-title" v-model="album.title" class="form-control">
            <div class="form-text">A slug will be automatically generated from the title</div>
        </div>
        <div class="mb-3">
            <label for="album-category" class="form-label">Category</label>
            <select id="album-category" v-model="album.category" class="form-control">
                <option :value="null">None</option>
                <option v-for="cat in catStore.categories" :value="cat.id">{{ cat.name }}</option>
            </select>
        </div>
        <div class="mb-3">
            <label for="album-location" class="form-label">Location</label>
            <select id="album-location" v-model="album.location" class="form-control">
                <option :value="null">None</option>
                <option v-for="loc in locStore.locations" :value="loc.id">{{ loc.name }}</option>
            </select>
        </div>
        <div class="mb-3">
            <label for="album-description" class="form-label">Album Description</label>
            <textarea id="album-description" cols="30" rows="10" v-model="album.description" class="form-control"></textarea>
        </div>

        <button type="submit" class="btn btn-success">Save Album</button>
    </form>

    <div class="mb-3">
        <label for="file-upload">Upload Images</label>
        <input type="file" multiple class="form-control" id="file-upload" ref="fileUpload">
    </div>
    <div class="container">
        <div class="row image-previews" ref="imagePreview"></div>
    </div>
</template>

<style>
.image-preview {
    max-width: 100%;
}
</style>