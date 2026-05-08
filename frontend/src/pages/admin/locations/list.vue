<script setup>
import {onMounted, ref} from "vue";
import {useLocationStore} from "../../../store/locations.js";

const locStore = useLocationStore();

onMounted(() => {
    locStore.getLocations();
});

const newLocation = ref({
    name: '',
    coords: null,
});
function saveNewLocation() {
    saveLocation(newLocation.value)
        .then(() => {
            newLocation.value.name = '';
            newLocation.value.coords = null;
        });
}
async function saveLocation(loc) {
    if (loc.saving) return;
    loc.saving = true;
    let locCopy = loc;
    if (loc.hasOwnProperty('_edit'))
        locCopy = loc._edit;
    if (locCopy.coords) {
        const floats = locCopy.coords.split(',').map(c => parseFloat(c) || null);
        [locCopy.coordinate_lat, locCopy.coordinate_lng] = floats;
    }

    await locStore.saveLocation(locCopy);
    loc.saving = false;
    loc.edit = false;
}

function editLocation(loc) {
    loc._edit = JSON.parse(JSON.stringify(loc));
    loc._edit.coords = loc.coordinate_lat+','+loc.coordinate_lng;
    loc.edit = true;
}
function cancelEdit(loc) {
    loc.edit = false;
}
</script>

<template>
    <table class="table">
        <thead>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Coordinates</th>
            <th>Albums</th>
            <th></th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="loc in locStore.locations" :key="loc.id">
            <td>{{ loc.id }}</td>
            <td>
                <input v-if="loc.edit" type="text" v-model="loc._edit.name" :disabled="loc.saving"
                       class="form-control" @keyup.enter="saveLocation(loc)" @keyup.esc="cancelEdit(loc)">
                <span v-else @dblclick="editLocation(loc)">{{ loc.name }}</span>
            </td>
            <td>
                <template v-if="loc.edit">
                    <input type="text" v-model="loc._edit.coords" :disabled="loc.saving"
                        class="form-control" @keyup.enter="saveLocation(loc)" @keyup.esc="cancelEdit(loc)">
                </template>
                <span v-else-if="loc.coordinate_lat" @dblclick="editLocation(loc)">
                    {{ loc.coordinate_lat }}, {{ loc.coordinate_lng }}
                </span>
            </td>
            <td>{{ loc.num_albums }}</td>
            <td class="text-end">
                <button v-if="!loc.edit" class="btn btn-info" @click="editLocation(loc)">🖉</button>
                <button v-else class="btn btn-success" :disabled="loc.saving"
                        @click="saveLocation(loc)">✓</button>
                <button class="btn btn-outline-danger ms-3" @click="locStore.deleteLocation(loc.id)">🗑</button>
            </td>
        </tr>
        </tbody>
    </table>
    <form @submit.prevent="saveNewLocation()" class="row row-cols-lg-auto g-3 align-items-center">
        <div class="col-12">
            <label for="new-loc-name" class="visually-hidden">Location name</label>
            <input type="text" v-model="newLocation.name" class="form-control" id="new-cat-name" placeholder="Location name">
        </div>
        
        <div class="col-12">
            <label for="new-loc-lat" class="visually-hidden">Latitude</label>
            <input type="text" v-model="newLocation.coords" class="form-control" id="new-loc-lat" placeholder="Latitude,Longitude">
        </div>

        <div class="col-12">
            <button type="submit" class="btn btn-primary">Create</button>
        </div>
    </form>
</template>

<style scoped>

</style>