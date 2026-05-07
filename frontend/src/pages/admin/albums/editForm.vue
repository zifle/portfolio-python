<script setup>
import {useAdminAlbumStore} from "../../../store/admin/albums.js";
import {computed, onMounted, ref, watch} from "vue";
import {useCategoryStore} from "../../../store/categories.js";
import {useLocationStore} from "../../../store/locations.js";
import Items from "./items.vue";

const albumStore = useAdminAlbumStore();
const catStore = useCategoryStore();
const locStore = useLocationStore();

const {album} = defineProps(['album']);
const emit = defineEmits(['albumSaved', 'albumItems']);

onMounted(() => {
    catStore.getCategories();
    locStore.getLocations();
})

const saving = ref(false);
const tmp_album_items = ref([]);
async function saveAlbum() {
    saving.value = true;
    try {
        const copy = JSON.parse(JSON.stringify(album));
        copy.items = tmp_album_items.value.map(item => ({id: item.id, order: item.order}));
        const new_album = await albumStore.saveAlbum(copy);
        if (new_album) {
            emit("albumSaved", new_album);
        }
    } finally {
        saving.value = false;
    }
}

// watch(() => {
//     console.log('tmp_album_items', tmp_album_items.value);
// })

const locDistances = ref([])
const locations = computed(() => {
    // Clone the stores location list, so we can manipulate the props
    // without tempering with the original list
    const locs = JSON.parse(JSON.stringify(locStore.locations));
    for (let loc of locDistances.value) {
        const _loc = locs.find(_loc => _loc.id === loc.id);
        if (_loc) {
            _loc.distance = loc.distance;
        }
    }
    locs.sort((a, b) => {
        if (a.hasOwnProperty('distance') && b.hasOwnProperty('distance')) {
            return a.distance - b.distance;
        } else if (a.hasOwnProperty('distance')) {
            return -1;
        } else if (b.hasOwnProperty('distance')) {
            return 1;
        }
        return 0;
    });
    return locs;
});
function setLocDistances(locations) {
    locDistances.value = locations;
    if (!album.location && locations.length > 0) {
        album.location = locations[0].id;
    }
}

const cameras = ref([])
const lenses = ref([])
const suggested_tags = computed(() => {
    const list = [];
    for (let camera of cameras.value) {
        list.push(camera.brand +' '+ camera.model);
    }
    for (let lens of lenses.value) {
        list.push(lens.brand +' '+ lens.model);
    }
    return list;
});

function checkAndSetDates(dates) {
    if (album.date_start != null || album.date_end != null) {
        return;
    }
    const len = dates.length;
    if (len > 0) {
        if (len === 1) {
            // We have just one date for all images, use this!
            album.date_start = dates[0];
            album.date_end = dates[0];
        } else {
            let first_date = null;
            let last_date = null;
            let has_null = false;
            for (let date of dates) {
                if (date == null) {
                    has_null = true;
                }
                let dt = new Date(date);
                if (first_date == null || first_date > dt) {
                    first_date = dt;
                }
                if (last_date == null || last_date < dt) {
                    last_date = dt;
                }
            }
            let days_delta = (last_date - first_date) / 1000 / 86400;
            if (days_delta < 7 && !has_null) {
                album.date_start = first_date.toISOString().split('T')[0];
                album.date_end = last_date.toISOString().split('T')[0];
            }
        }
    }
}

function imagesUploaded(data) {
    if (data.hasOwnProperty('images')) {
        emit('albumItems', [...album.items, ...data.images]);
    }

    if (data.hasOwnProperty('locations')) {
        setLocDistances(data.locations);
    }
    if (data.hasOwnProperty('cameras')) {
        cameras.value = data.cameras;
    }
    if (data.hasOwnProperty('lenses')) {
        lenses.value = data.lenses;
    }
    if (data.hasOwnProperty('dates')) {
        checkAndSetDates(data.dates);
    }
}

async function insertIntoDescription(text) {
    // todo
    document.getElementById('album-description');
}


</script>

<template>
    <h2>
        <template v-if="album.id">Edit {{ album.title }}</template>
        <template v-else>Create new album</template>
    </h2>
    <form @submit.prevent="saveAlbum" class="mb-3">
        <div class="row">
            <div class="mb-3 col-lg-10">
                <label for="album-title" class="form-label">Album Title</label>
                <input type="text" id="album-title" v-model="album.title" class="form-control">
                <div class="form-text">A slug will be automatically generated from the title</div>
            </div>
            <div class="mb-3 col-lg-2 align-content-center">
                <div class="form-check">
                    <input type="checkbox" class="form-check-input" id="album-published" v-model="album.published">
                    <label for="album-published" class="form-check-label">Published</label>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="mb-3 col-lg-6">
                <label for="album-date-start" class="form-label">Start Date</label>
                <input type="date" v-model="album.date_start" class="form-control"
                        id="album-date-start">
            </div>
            <div class="mb-3 col-lg-6">
                <label for="album-date-end" class="form-label">End Date</label>
                <input type="date" v-model="album.date_end" class="form-control"
                        id="album-date-end">
            </div>
        </div>
        <div class="row">
            <div class="mb-3 col-lg-6">
                <label for="album-category" class="form-label">Category</label>
                <select id="album-category" v-model="album.category" class="form-select">
                    <option :value="null">None</option>
                    <option v-for="cat in catStore.categories" :value="cat.id">{{ cat.name }}</option>
                </select>
            </div>
            <div class="mb-3 col-lg-6">
                <label for="album-location" class="form-label">Location</label>
                <select id="album-location" v-model="album.location" class="form-select">
                    <option :value="null">None</option>
                    <option v-for="loc in locations" :value="loc.id">
                        {{ loc.name }}
                        <template v-if="loc.hasOwnProperty('distance')">
                            - {{ loc.distance.toFixed(2) }}km away
                        </template>
                    </option>
                </select>
            </div>
        </div>
        <div class="mb-3">
            <label for="album-description" class="form-label">Album Description</label>
            <textarea id="album-description" cols="30" rows="10" v-model="album.description"
                      class="form-control"></textarea>
            <div class="form-text">
                <span v-for="tag in suggested_tags" @click="insertIntoDescription(tag)"
                      class="badge text-bg-secondary clickable me-2">
                    {{ tag }}
                </span>
            </div>
        </div>

        <button type="submit" class="btn btn-success" :disabled="saving">Save Album</button>
        <span v-if="saving">Saving ...</span>
    </form>

    <h4>Album items</h4>
    <items class="mt-4"
           :items="album.items" @files-uploaded="imagesUploaded"
           @album-items="(itms) => emit('albumItems', itms)"
           @list-items="(itms) => tmp_album_items = itms"></items>
</template>

<style scoped>

</style>