<script setup>
import {onMounted, ref} from "vue";
import {useLocationStore} from "../../../store/locations.js";

const locStore = useLocationStore();

onMounted(() => {
    locStore.getLocations();
});

const newLocation = ref({
    name: '',
    coordinate_lat: null,
    coordinate_lng: null,
});
function saveNewCategory() {
    locStore.saveLocation(newLocation.value)
        .then(() => {
            newLocation.value.name = '';
            newLocation.value.coordinate_lat = null;
            newLocation.value.coordinate_lng = null;
        });
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
            <td>{{ loc.name }}</td>
            <td>
                <template v-if="loc.coordinate_lat">
                    {{ loc.coordinate_lat }}, {{ loc.coordinate_lng }}
                </template>
            </td>
            <td>{{ loc.num_albums }}</td>
            <td>
                <button class="btn btn-outline-danger" @click="locStore.deleteLocation(cat.id)">&#128465;</button>
            </td>
        </tr>
        </tbody>
    </table>
    <form @submit.prevent="saveNewCategory()" class="row row-cols-lg-auto g-3 align-items-center">
        <div class="col-12">
            <label for="new-loc-name" class="visually-hidden">Category name</label>
            <input type="text" v-model="newLocation.name" class="form-control" id="new-cat-name" placeholder="Location name">
        </div>
        
        <div class="col-12">
            <label for="new-loc-lat" class="visually-hidden">Latitude</label>
            <input type="text" v-model="newLocation.coordinate_lat" class="form-control" id="new-cat-lat" placeholder="Latitude">
        </div>

        <div class="col-12">
            <label for="new-loc-lng" class="visually-hidden">Longitude</label>
            <input type="text" v-model="newLocation.coordinate_lng" class="form-control" id="new-cat-lng" placeholder="Longitude">
        </div>

        <div class="col-12">
            <button type="submit" class="btn btn-primary">Create</button>
        </div>
    </form>
</template>

<style scoped>

</style>