<script setup>
import {onMounted, onUnmounted, ref, useTemplateRef} from "vue";
import {useAdminAlbumStore} from "../../../store/admin/albums.js";

const albumStore = useAdminAlbumStore();

const emit = defineEmits(['filesUploaded']);

const fileUpload = useTemplateRef('fileUpload');
const uploading = ref(false);
onMounted(() => {
    fileUpload.value.addEventListener("change", (e) => {
        const files = e.target.files;
        uploadImages(files);
    });
});

async function uploadImages(files) {
    uploading.value = true;

    try {
        const data = new FormData();

        let idx = 0;
        for (const file of files) {
            if (!file.type.startsWith("image/")) {
                continue;
            }

            data.append('file_' + idx, file);
            idx++;
        }

        if (idx > 0) {
            const upload_data = await albumStore.uploadImages(data);
            emit('filesUploaded', upload_data);
        } else {
            console.warn('Empty file list!', files);
        }
    } finally {
        uploading.value = false;
    }
}

const dropZone = useTemplateRef('fileDropZone');
function dragoverFile(e) {
    const fileItems = [...e.dataTransfer.items].filter( i => i.kind === 'file');
    if (fileItems.length > 0) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
        dropZone.value.classList.remove('d-none');
    } else {
        dropZone.value.classList.add('d-none');
    }
}
function dropFiles(e) {
    const fileItems = [...e.dataTransfer.items].filter( i => i.kind === 'file');
    if (fileItems.length > 0) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
        uploadImages(fileItems.map(i => i.getAsFile()));
        dragEnd();
    }
}
function dragEnd() {
    dropZone.value.classList.add('d-none');
}
onMounted(() => {
    document.body.addEventListener('dragover', dragoverFile);
    document.body.addEventListener('dragend', dragEnd);
    document.body.addEventListener('dragleave', dragEnd);
    dropZone.value.addEventListener('drop', dropFiles);
});
onUnmounted(() => {
    document.body.removeEventListener('dragover', dragoverFile);
    document.body.removeEventListener('dragend', dragEnd);
    document.body.removeEventListener('dragleave', dragEnd);
})
</script>

<template>
    <div class="mt-3 mb-3">
        <label for="file-upload">Upload Images</label>
        <input type="file" multiple class="form-control" id="file-upload" ref="fileUpload">
    </div>

    <div v-if="uploading" class="uploading position-fixed">
        Uploading images ...
    </div>

    <div class="file-dropzone d-none" ref="fileDropZone">+</div>
</template>

<style scoped>
.file-dropzone {
    position: fixed;
    display: flex;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    align-items: center;
    justify-content: center;
    font-size: 20rem;
    user-select: none;
}

.uploading {
    bottom: 20px;
    right: 20px;
    padding: 10px 20px;
    background-color: var(--bs-body-bg);
    border: 2px solid var(--bs-border-color);
}
</style>