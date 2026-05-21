<script setup>
import {onMounted, onUnmounted, ref, useTemplateRef} from "vue";
import {useAdminAlbumStore} from "../../../store/admin/albums.js";
import { useLocationStore } from "../../../store/locations.js";
import ExifReader from 'exifreader';

const albumStore = useAdminAlbumStore();

const emit = defineEmits(['filesUploaded', 'locations', 'dates']);

const uploadIndividually = true;

const fileUpload = useTemplateRef('fileUpload');
const uploading = ref(false);
onMounted(() => {
    fileUpload.value.addEventListener("change", (e) => {
        const files = e.target.files;
        uploadImages(files);
    });
});

async function uploadImages(files) {
    if (uploadIndividually) {
        return uploadImagesIndividually(files);
    }

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

async function uploadImagesIndividually(files) {
    uploading.value = true;

    try {
        const props = await getImageDuplicationProps(files);
        const check = await albumStore.checkImageDuplicates(props);
        if (check.hasOwnProperty('locations')) {
            emit('filesUploaded', check);
        }

        if (check.hasOwnProperty('upload') && check.upload.length === 0) {
            // All images are already on the server, no need to send them again
            return;
        }

        let coords = [];
        const dates = [];
        const uploadsPromises = [];
        for (const file of files) {
            if (!file.type.startsWith('image/')) {
                continue;
            }
            if (!check.upload.includes(file.name)) {
                continue;
            }

            const data = new FormData();
            data.append('img', file);
            const prom = albumStore.uploadImages(data).then(upload_data => {
                coords = [...coords, ...upload_data.coords];
                if (upload_data.date !== null)
                    dates.push(upload_data.date);
                emit('filesUploaded', upload_data);
            });
            uploadsPromises.push(prom);
        }
        await Promise.all(uploadsPromises);
        if (coords.length > 0) {
            const locStore = useLocationStore();
            locStore.getNearbyLocations(coords).then(locations => {
                emit('locations', locations);
            });
        }
        if (dates.length > 0) {
            emit('dates', dates.filter((val, idx, arr) => arr.indexOf(val) === idx))
        }
    } finally {
        uploading.value = false;
    }
}

async function getImageDuplicationProps(files) {
    const promises = [];
    for (const file of files) {
        if (!file.type.startsWith('image/')) {
            continue;
        }
        const prom = new Promise(async (res) => {
            const exif = await ExifReader.load(file);

            let dt = new Date(file.lastModified);
            let date;
            if (exif.hasOwnProperty('DateTimeOriginal')) {
                date = exif.DateTimeOriginal.description;
            } else if (exif.hasOwnProperty('DateTimeDigitized')) {
                date = exif.DateTimeDigitized.description;
            } else if (exif.hasOwnProperty('DateTime')) {
                date = exif.DateTime.description;
            }
            if (date) {
                // Fix the date format (uses : instead of - to separate y-m-d)
                let [d, t] = date.split(' ');
                d = d.replaceAll(':', '-');
                date = d+'T'+t
            }

            let offset = '+0000';
            if (exif.hasOwnProperty('OffsetTimeOriginal')) {
                offset = exif.OffsetTimeOriginal.description.replace(':', '');
            } else if (exif.hasOwnProperty('OffsetTime')) {
                offset = exif.OffsetTime.description.replace(':', '');
            }
            
            const date_taken = (new Date(date+offset)).toISOString();

            let location = null;
            if (exif.hasOwnProperty('GPSLatitude') && exif.hasOwnProperty('GPSLongitude')) {
                location = [parseFloat(exif.GPSLatitude.description), parseFloat(exif.GPSLongitude.description)];
            }

            res({filename: file.name, date_taken, location});
        });
        promises.push(prom);
    }
    const props = await Promise.all(promises);
    return props;
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