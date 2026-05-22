<script setup>
import {debounce} from "../utils/debounce.js";
import {computed, onUpdated, ref, useTemplateRef, watch} from "vue";
import {toggleGigante} from "../utils/gigante/gigante.js";

const {'items': albumItems, loading} = defineProps(['items', 'loading']);
const emit = defineEmits(['imgLoaded'])

const images = useTemplateRef('images');

watch(() => {
    if (loading) {
        const items = images.value.querySelectorAll('.image,.text-box');
        for (let item of items) {
            item.classList.add('opacity-0');
        }
    }
});
function stopLoading() {
    if (images.value !== null) {
        const items = images.value.querySelectorAll('.image,.text-box');
        for (let item of items) {
            item.classList.remove('opacity-0');
        }
    }
}
onUpdated(() => {
    const imgs = images.value.querySelectorAll('img');
    const imgLoadPromises = [];
    for (let img of imgs) {
        if (!img.complete) {
            imgLoadPromises.push(new Promise(res => {
                img.onload = () => res();
            }));
        } else {
            imgLoadPromises.push(true);
        }
    }
    if (imgLoadPromises.length > 0) {
        Promise.all(imgLoadPromises).then(() => {
            emit('imgLoaded');
            stopLoading();
        });
    }
});

const getNumCols = () => {
    const vw = window.innerWidth;
    let cols = 1;
    if (vw >= 800 && vw < 1200) {
        cols = 3;
    } else if (vw >= 1200 && vw < 1600) {
        cols = 4;
    } else if (vw >= 1600) {
        cols = 5;
    }
    return cols
}
const numCols = ref(getNumCols());
const resizeDB = debounce(() => {
    numCols.value = getNumCols();
}, 50);
window.addEventListener('resize', resizeDB);

const items = computed(() => {
    const rtn = [];
    const vw = window.innerWidth;
    const cols = numCols.value;
    const colWidth = vw/cols;
    let col = 0;
    for (let item of albumItems) {
        let _item = {
            order: item.order,
            gridSize: 1,
            col
        }
        col += 1;
        if (col >= cols) col = 0;
        if (item.hasOwnProperty('paths')) {
            let srcset = [];
            let sizes = [];
            let max_width = item.max_width;
            let min_width = max_width;
            for (let width in item.paths) {
                if (item.paths.hasOwnProperty(width)) {
                    const w = parseInt(width);
                    if (w < min_width) {
                        min_width = w;
                    }
                    srcset.push(`${item.paths[width]} ${width}w`);
                }
            }
            // The _slot_ part of the `sizes` simply needs to know how
            // big the image will display
            let maxImgWidth = colWidth * _item.gridSize;
            if (cols < _item.gridSize) {
                maxImgWidth = vw;
            }
            let width = maxImgWidth;
            for (let w in item.paths) {
                const wNum = parseInt(w);
                if (item.paths.hasOwnProperty(w) && wNum >= maxImgWidth) {
                    if (wNum < width) {
                        width = wNum;
                    }
                }
            }

            _item['type'] = 'image';
            _item['srcset'] = srcset.join(',');
            _item['sizes'] = 100/cols+'vw';
            _item['src'] = item.paths[width];
            _item['desc'] = item.description || 'Photo#'+item.order;
        } else if (item.hasOwnProperty('description')) {
            _item['type'] = 'text';
            _item['description'] = item.description;
        }
        rtn.push(_item);
    }
    return rtn.toSorted((a,b) => a.order - b.order);
});
const colItems = computed(() => {
    const cols = Array.apply(null, Array(numCols.value)).map(() => []);
    for (let item of items.value) {
        cols[item.col].push(item);
    }
    return cols;
});
</script>

<template>
    <div class="images masonry wrapper switcher" ref="images">
        <div v-for="col in colItems" class="flow">
            <div v-for="item of col" class="image-container">
                <img v-if="item.type === 'image'" :srcset="item.srcset" :sizes="item.sizes" :src="item.src"
                    class="image w-100 opacity-0" @click="toggleGigante($event, item)" :alt="item.desc">
                <p v-else-if="item.type === 'text'" class="text-box opacity-0">{{ item.description }}</p>
            </div>
        </div>
    </div>
    <div id="view-container-container" class="d-none">
        <div id="view-container"></div>
    </div>
</template>

<style lang="scss">
// Items styling
@media screen and (min-width: 800px) {
    body[data-bs-theme="dark"] .image-container {
        filter: contrast(80%) brightness(80%) grayscale(30%);
    }

    .image-container {
        transition: 0.2s filter linear;
        filter: contrast(70%) brightness(100%) grayscale(30%);
    }

    .image-container:hover {
        filter: contrast(100%) brightness(100%) grayscale(0%) !important;
    }
}

.image-container > img:not(.opacity-0), .loading-spinner:not(.opacity-0) {
    transition: opacity .3s;
}

.text-box {
    white-space: pre-wrap;
}


// CSS Masonry
.masonry {
    --gutter: 0.25em;
    --flow-space: var(--gutter);
    --switcher-target-container-width: 45rem;

    img {
        width: 100%;
    }
}

.switcher {
    display: flex;
    flex-wrap: wrap;
    gap: var(--gutter, 1em);
    align-items: var(--switcher-vertical-alignment, flex-start);

    > * {
        flex-grow: 1;
        flex-basis: calc(
            (var(--switcher-target-container-width, 40rem) - 100%) * 999
        );
    }
}

.flow > * + * {
    margin-block-start: var(--flow-space, 1em);
}

.wrapper {
    margin-inline: auto;
    padding-inline: var(--gutter);
}
</style>