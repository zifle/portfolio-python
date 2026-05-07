<script setup>
import {computed} from "vue";

const {album, loading} = defineProps(['album', 'loading']);

const useIcons = false;
const dateFormatter = new Intl.DateTimeFormat(navigator.language, {
    dateStyle: 'long',
});

const date_start = computed(() => {
    if (!album.date_start) {
        return null;
    }
    return dateFormatter.format(new Date(album.date_start));
})
const date_end = computed(() => {
    if (!album.date_end) {
        return null;
    }
    const de = dateFormatter.format(new Date(album.date_end));
    if (date_start.value != null && date_start.value == de) {
        return null;
    }
    return de;
});

</script>

<template>
    <div class="album-intro container">
        <template v-if="album">
            <div class="row">
                <h2 class="text-center">{{ album.title }}</h2>
                <p class="album-date-loc text-center">
                    <span v-if="date_start" class="album-date">
                        <template v-if="useIcons">🗓️</template>
                        <time :datetime="album.date_start">{{ date_start }}</time>
                        <span v-if="date_start && date_end"> - </span>
                        <time v-if="date_end" :datetime="album.date_end">{{ date_end }}</time>
                    </span>
                    <span v-if="date_start && album.location_name" class="ms-3 me-3">|</span>
                    <span v-if="album.location_name">
                        <template v-if="useIcons">🗺️</template> {{ album.location_name }}
                    </span>
                </p>
            </div>
            <div class="row" v-if="album.description">
                <p class="album-description">{{ album.description }}</p>
            </div>
            <div class="row" v-if="album.tags">
                <div class="col text-end">
                    <span v-for="tag in album.tags" class="badge text-secondary">{{ tag }}</span>
                </div>
            </div>
        </template>
    </div>
</template>

<style scoped>
.album-description {
    white-space: pre-wrap;
}
</style>