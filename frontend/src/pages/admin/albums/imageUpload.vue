<script setup>
import {onMounted, ref, useTemplateRef} from "vue";
import {useAdminAlbumStore} from "../../../store/admin/albums.js";

const albumStore = useAdminAlbumStore();

const emit = defineEmits(['filesUploaded']);

const fileUpload = useTemplateRef('fileUpload');
const uploading = ref(false);
onMounted(() => {
    fileUpload.value.addEventListener("change", async (e) => {
        uploading.value = true;
        try {
            const files = e.target.files;
            const data = new FormData();

            let idx = 0;
            for (const file of files) {
                if (!file.type.startsWith("image/")) {
                    continue;
                }

                data.append('file_' + idx, file);
                idx++;
            }

            const upload_data = await albumStore.uploadImages(data);
            emit('filesUploaded', upload_data);
        } finally {
            uploading.value = false;
        }
    });
});
</script>

<template>
    <div class="mt-3 mb-3">
        <label for="file-upload">Upload Images</label>
        <input type="file" multiple class="form-control" id="file-upload" ref="fileUpload">
    </div>

    <div v-if="uploading" class="uploading position-fixed">
        Uploading images ...
    </div>
</template>

<style scoped>

</style>