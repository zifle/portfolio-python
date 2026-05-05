<script setup>
import {useCategoryStore} from "../../../store/categories.js";
import {onMounted, ref} from "vue";

const catStore = useCategoryStore();

onMounted(() => {
    catStore.getCategories();
});

const newCategory = ref({
    name: '',
    order: 0
});
function saveNewCategory() {
    catStore.saveCategory(newCategory.value)
        .then(() => {
            newCategory.value.name = '';
            newCategory.value.order = 0;
        });
}
</script>

<template>
    <table class="table">
        <thead>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Albums</th>
            <th></th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="cat in catStore.categories" :key="cat.id">
            <td>{{ cat.id }}</td>
            <td>{{ cat.name }}</td>
            <td>{{ cat.num_albums }}</td>
            <td>
                <button class="btn btn-outline-danger" @click="catStore.deleteCategory(cat.id)">&#128465;</button>
            </td>
        </tr>
        </tbody>
    </table>
    <form @submit.prevent="saveNewCategory()" class="row row-cols-lg-auto g-3 align-items-center">
        <div class="col-12">
            <label for="new-cat-name" class="visually-hidden">Category name</label>
            <input type="text" v-model="newCategory.name" class="form-control" id="new-cat-name" placeholder="Category name">
        </div>
        
        <div class="col-12">
            <label for="new-cat-order" class="visually-hidden">Order</label>
            <input type="number" v-model="newCategory.order" class="form-control" id="new-cat-order">
        </div>

        <div class="col-12">
            <button type="submit" class="btn btn-primary">Create</button>
        </div>
    </form>
</template>

<style scoped>

</style>