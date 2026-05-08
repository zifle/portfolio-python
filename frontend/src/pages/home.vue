<script setup>
import {useAuthStore} from '../store/auth.js'
import {useRouter} from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

async function logout() {
    try {
        await authStore.logout(router)
    } catch (err) {
        console.error(err);
    }
}

authStore.fetchUser()
</script>

<template>
    <div class="container">
        <div class="row">
            <div class="col">
                <h1 class="text-center">Welcome to my portfolio!</h1>
            </div>
        </div>
        <div class="row">
            <div class="col text-center">Please check out my photos, by clicking any of the albums in the menu!</div>
        </div>
    </div>
</template>