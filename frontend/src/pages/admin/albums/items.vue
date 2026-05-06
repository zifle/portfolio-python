<script setup>
import {computed, onMounted, ref, useTemplateRef} from "vue";
import {useAdminAlbumStore} from "../../../store/admin/albums.js";

const albumStore = useAdminAlbumStore();
const {'items': album_items} = defineProps(['items'])
const emit = defineEmits(['filesUploaded', 'albumItems', 'listItems']);

const itemsList = computed(() => {
    const final_items = [];
    let order = 0;
    for (let item of album_items) {
        order = item.order ?? order+1;

        let _item = {
            id: item.id,
            order: order,
        };
        if (item.hasOwnProperty('paths')) {
            let srcset = [];
            let sizes = [];
            let max_width = item.max_width;
            for (let width in item.paths) {
                if (item.paths.hasOwnProperty(width)) {
                    srcset.push(`${item.paths[width]} ${width}w`);
                    // todo We could check whether we're in a viewport
                    //       that uses a smaller column size for the
                    //       images, and thus specify a better width
                    sizes.push(`(width <= ${width}px) ${width}px`);
                }
            }
            _item['type'] = 'image';
            _item['srcset'] = srcset.join(',');
            _item['sizes'] = sizes.join(',');
            _item['src'] = item.paths[max_width];
        } else if (item.hasOwnProperty('text')) {
            _item['type'] = 'text';
            _item['text'] = item.text;
        }
        if (_item !== null)
            final_items.push(_item);
    }
    final_items.sort((a, b) => a.order - b.order);
    emit('listItems', final_items);
    return final_items;
});

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

function removeItem(item) {
    const new_list = [];
    for (const itm of album_items) {
        if (itm.id !== item.id) {
            new_list.push(itm)
        }
    }
    emit('albumItems', new_list);
}
</script>

<template>
    <div class="row images">
        <div v-for="itm of itemsList" class="col-lg-3 col-6 mb-3 has-hover-controls">
            <div class="hover-controls">
                <span class="badge text-bg-danger clickable" @click="removeItem(itm)">X</span>
            </div>

            <img loading="lazy" :srcset="itm.srcset" :sizes="itm.sizes" :src="itm.src"
                 class="image-preview" v-if="itm.type =='image'">
            <pre v-else-if="itm.type =='text'">{{ itm.text }}</pre>
        </div>
    </div>

    <div class="mt-3 mb-3">
        <label for="file-upload">Upload Images</label>
        <input type="file" multiple class="form-control" id="file-upload" ref="fileUpload">
    </div>
</template>

<style scoped>
.image-preview {
    max-width: 100%;
}

.hover-controls {
    position: absolute;
    top: 0;
    right: 0;
    display: none;
}

.has-hover-controls {
    position: relative;
}
.has-hover-controls:hover > .hover-controls {
    display: block;
}
</style>