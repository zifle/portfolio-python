import { createApp } from 'vue'
import './style.css'
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

app.mount('#app')
