<script setup>
import {useAdminAlbumStore} from '../../../store/admin/albums';
import {onMounted} from "vue";

const albumStore = useAdminAlbumStore()
onMounted(() => {
    albumStore.getAlbums();
});
</script>

<template>
    <table class="table">
        <thead>
        <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Images</th>
            <th>Published</th>
            <th></th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="album in albumStore.albums" :key="album.id">
            <td>{{ album.id }}</td>
            <td>{{ album.title }}</td>
            <td>{{ album.num_images }}</td>
            <td>
                <button type="button" class="btn btn-sm" @click="albumStore.togglePublished(album)"
                    :class="{'btn-outline-success': album.published, 'btn-outline-danger': !album.published}">
                    <span v-if="album.published" class="text-success">✓</span>
                    <span v-else class="text-danger">𐄂</span>
                </button>
            </td>
            <td>
                <router-link :to="{name: 'admin-album-edit', params: {id: album.id}}" class="btn btn-outline-info">
                    🖉
                </router-link>
            </td>
        </tr>
        </tbody>
    </table>
</template>

<style scoped>

</style>