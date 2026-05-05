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
    <div class="d-flex justify-content-center align-items-center">
        <div class="login">
            <form @submit.prevent="login">
                <div class="mb-3">
                    <label for="username" class="form-label">Username</label>
                    <input type="text" name="username" v-model="username" required @input="resetError"
                        class="form-control" id="username"/>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" name="password" v-model="password" required @input="resetError"
                        class="form-control" id="password"/>
                </div>
                <button class="btn btn-primary">Login</button>
            </form>
            <p v-if="error" class="text-danger">{{ error }}</p>
        </div>
    </div>
</template>

<style scoped>
.login {

}
</style>