<script setup lang="ts">
import {onMounted, ref} from "vue";
import EditForm from "./editForm.vue";

const album = ref({
    id: 0,
    title: '',
    items: []
});
onMounted(() => {
    album.value = {
        id: 0,
        title: '',
        slug: '',
        published: false,
        location: null,
        category: null,
        description: '',
        date_start: null,
        date_end: null,
        items: []
    }
})
</script>

<template>
    <edit-form :album="album" @album-items="(itms) => album.items = itms"></edit-form>
</template>

<style scoped>

</style>