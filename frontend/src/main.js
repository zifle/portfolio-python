import { createApp } from 'vue'
import './style.scss'
import './bootstrap.js'
import App from './App.vue'
import {createPinia} from "pinia";
import {useAuthStore} from './store/auth';
import router from './router'
const app = createApp(App);

const pinia = createPinia();
app.use(pinia);
app.use(router);

const authStore = useAuthStore();
authStore.setCsrfToken();

app.mount('#app');

// Set light-/dark-mode depending on user preference
(() => {
    let darkModeMql = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)');
    if (darkModeMql && darkModeMql.matches) {
        document.body.setAttribute('data-bs-theme', 'dark');
    } else {
        document.body.setAttribute('data-bs-theme', 'light');
    }
})();