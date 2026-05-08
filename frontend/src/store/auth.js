import {defineStore} from 'pinia';
import {ref} from "vue";
import {useAlbumStore} from "./albums.js";

export const useAuthStore = defineStore('auth', () => {
    const storedState = localStorage.getItem('authState');

    const isAuthenticated = ref(false);
    const user = ref(null);
    if (storedState) {
        const props = JSON.parse(storedState);
        user.value = props.user;
        isAuthenticated.value = props.isAuthenticated;
    }

    async function setCsrfToken() {
        await fetch('/auth/set-csrf-token', {
            method: 'GET',
            credentials: 'include'
        });
    }

    async function login(username, password, router = null) {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({
                username, password
            }),
            credentials: 'include'
        });
        const data = await response.json();
        if (data.success) {
            isAuthenticated.value = true;
            saveState();
            if (router) {
                await router.push({
                    name: 'admin'
                });
            }
            const albumStore = useAlbumStore();
            albumStore.getAlbums(true);
        } else {
            user.value = null;
            isAuthenticated.value = false;
            saveState();
        }
    }

    async function logout(router = null) {
        try {
            const response = await fetch('/auth/logout', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                },
                credentials: 'include',
            });
            if (response.ok) {
                user.value = null;
                isAuthenticated.value = false;
                saveState();
                if (router) {
                    await router.push({
                        name: 'home',
                    })
                }
                const albumStore = useAlbumStore();
                albumStore.getAlbums(true);
            }
        } catch (error) {
            console.error('Logout failed', error)
            throw error
        }
    }

    async function fetchUser() {
        try {
            const response = await fetch('/auth/user', {
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            });
            if (response.ok) {
                user.value = await response.json();
                isAuthenticated.value = true;
            } else {
                user.value = null;
                isAuthenticated.value = false;
            }
        } catch (err) {
            console.error('Failed to fetch user', err);
            user.value = null;
            isAuthenticated.value = false;
        }
        saveState();
    }

    function saveState() {
        localStorage.setItem('authState', JSON.stringify({
            user: user.value,
            isAuthenticated: isAuthenticated.value,
        }))
    }

    return {isAuthenticated, user, fetchUser, login, logout, setCsrfToken};
})

export function getCSRFToken() {
    /*
      We get the CSRF token from the cookie to include in our requests.
      This is necessary for CSRF protection in Django.
       */
    const name = 'csrftoken'
    let cookieValue = null
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim()
            if (cookie.substring(0, name.length + 1) === name + '=') {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }
    if (cookieValue === null) {
        throw 'Missing CSRF cookie.'
    }
    return cookieValue
}