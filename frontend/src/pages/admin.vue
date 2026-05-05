<script setup>

</script>

<template>
    <div class="container">
        <h4>Content Control Panel</h4>
        <ul class="nav nav-tabs mb-2">
            <li class="nav-item">
                <router-link :to="{name: 'admin-categories'}" class="nav-link" active-class="active">
                    Categories
                </router-link>
            </li>
            <li class="nav-item">
                <router-link :to="{name: 'admin-locations'}" class="nav-link" active-class="active">
                    Locations
                </router-link>
            </li>
            <li class="nav-item">
                <router-link :to="{name: 'admin-album-list'}" class="nav-link" active-class="active">
                    Albums
                </router-link>
            </li>
            <li class="nav-item">
                <router-link :to="{name: 'admin-album-create'}" class="nav-link" active-class="active">
                    Create new Album
                </router-link>
            </li>
        </ul>
        <router-view></router-view>
    </div>
</template>

<style scoped>

</style>