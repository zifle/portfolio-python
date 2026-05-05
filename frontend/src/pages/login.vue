<script setup>
import {useAuthStore} from "../store/auth.js";
import {ref} from "vue";
import {useRouter} from "vue-router";

const router = useRouter();
const authStore = useAuthStore();

const username = ref('');
const password = ref('');
const error = ref('');

const login = async function() {
    await authStore.login(username.value, password.value, router);
    if (!authStore.isAuthenticated) {
        this.error = 'Login failed. Please check your credentials.';
    }
}

const resetError = function() {
    error.value = '';
}
</script>

<template>
    <div class="login">
        <form @submit.prevent="login">
            <fieldset>
                <legend>Username</legend>
                <input type="text" name="username" v-model="username" required @input="resetError" />
            </fieldset>
            <fieldset>
                <legend>Password</legend>
                <input type="password" name="password" v-model="password" required @input="resetError" />
            </fieldset>
            <button>Login</button>
        </form>
        <p v-if="error" class="text-danger">{{ error }}</p>
    </div>
</template>