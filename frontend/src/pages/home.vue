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
    <h1>Welcome to home</h1>
    <p v-if="authStore.isAuthenticated">You are authed</p>
    <p v-else>You are not logged in. <router-link :to="{name:'login'}">Log in</router-link></p>
</template>