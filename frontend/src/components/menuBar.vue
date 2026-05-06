<script setup>
import {useAuthStore} from "../store/auth.js";
import {computed} from "vue";
import 'bootstrap/js/src/collapse.js';
import router from "../router/index.js";

const authStore = useAuthStore();
const isAdmin = computed(() => {
    return authStore.isAuthenticated;
});

</script>

<template>
    <nav class="navbar navbar-expand-lg">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">Niels Pedersen Photography</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <router-link :to="{name: 'home'}" class="nav-link" active-class="active">Home</router-link>
                    </li>

                </ul>
                <ul v-if="isAdmin" class="navbar-nav mb-2 mb-lg-0 d-flex justify-content-lg-end">
                    <li class="nav-item">
                        <router-link :to="{name: 'admin'}" class="nav-link" active-class="active">Admin</router-link>
                    </li>
                    <li class="nav-item">
                        <span class="nav-link clickable" @click="authStore.logout(router)" aria-label="Logout">
                            &#128682;
                            <span class="d-lg-none">Logout</span>
                        </span>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
</template>

<style scoped>

</style>