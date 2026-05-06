<script setup>
import {useAdminAlbumStore} from '../../../store/admin/albums';
import {onMounted} from "vue";

const albumStore = useAdminAlbumStore()
onMounted(() => {
    albumStore.getAlbums();
});

function deleteAlbum(album) {
    if (confirm('Are you sure you want to delete this album? This action CANNOT be reversed')) {
        albumStore.deleteAlbum(album.id);
    }
}
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
                <router-link :to="{name: 'admin-album-edit', params: {id: album.id}}"
                             class="btn btn-outline-info me-3">
                    🖉
                </router-link>
                <button :disabled="album.published" class="btn btn-outline-danger me-3"
                        @click="deleteAlbum(album)">&#128465;</button>
            </td>
        </tr>
        </tbody>
    </table>
</template>

<style scoped>

</style>