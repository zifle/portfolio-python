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

async function saveCategory(category) {
    if (category.saving) return;
    category.saving = true;
    let catCopy = category;
    if (category.hasOwnProperty('_edit')) {
        catCopy = category._edit;
    }

    await catStore.saveCategory(catCopy);
    category.saving = false;
    category.edit = false;
}

function editCategory(category) {
    category._edit = JSON.parse(JSON.stringify(category));
    category.edit = true;
}
function cancelEdit(category) {
    category.edit = false;
}
</script>

<template>
    <table class="table">
        <thead>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Order</th>
            <th>Albums</th>
            <th></th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="cat in catStore.categories" :key="cat.id">
            <td>{{ cat.id }}</td>
            <td>
                <input v-if="cat.edit" type="text" v-model="cat._edit.name" :disabled="cat.saving"
                        class="form-control" @keyup.enter="saveCategory(cat)" @keyup.esc="cancelEdit(cat)">
                <span v-else @dblclick="editCategory(cat)">{{ cat.name }}</span>
            </td>
            <td>
                <input v-if="cat.edit" type="number" v-model="cat._edit.order" :disabled="cat.saving"
                        class="form-control" @keyup.enter="saveCategory(cat)" @keyup.esc="cancelEdit(cat)">
                <span v-else @dblclick="editCategory(cat)">{{ cat.order }}</span>
            </td>
            <td>{{ cat.num_albums }}</td>
            <td class="text-end">
                <button v-if="!cat.edit" class="btn btn-info" @click="editCategory(cat)">🖉</button>
                <button v-else class="btn btn-success" :disabled="cat.saving"
                        @click="saveCategory(cat)">✓</button>
                <button class="btn btn-outline-danger ms-3" @click="catStore.deleteCategory(cat.id)">🗑</button>
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