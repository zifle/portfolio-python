<script setup>
import Masonry from 'masonry-layout';
import {onBeforeRouteUpdate, useRoute} from "vue-router";
import {computed, onMounted, onUpdated, ref, useTemplateRef} from "vue";
import {useAlbumStore} from "../store/albums.js";
import {debounce} from "../utils/debounce.js";

const route = useRoute();
const albumStore = useAlbumStore();

const images = useTemplateRef('images');
let masonry = null;
const album = ref(null)
onMounted(() => {
    albumStore.getAlbum(route.params.slug)
        .then(a => {
            album.value = a;
        });
});

onBeforeRouteUpdate((to, from) => {
    startLoading();

    albumStore.getAlbum(to.params.slug)
        .then(a => {
            album.value = a;
        });
});

function startLoading(cls = 'opacity-100') {
    const imgs = images.value.querySelectorAll('img');
    for (let img of imgs) {
        img.classList.add('opacity-0');
    }
    loadSpinner.value.classList.remove('opacity-0');
    loadSpinner.value.classList.remove('d-none');
}
function stopLoading() {
    const imgs = images.value.querySelectorAll('img');
    for (let img of imgs) {
        img.classList.remove('opacity-0');
    }
    loadSpinner.value.classList.add('opacity-0');
    setTimeout(() => {
        loadSpinner.value.classList.add('d-none');
    }, 300);
}

const loadSpinner = useTemplateRef('load-spinner');
onUpdated(() => {
    if (masonry) {
        masonry.reloadItems(images.value.querySelectorAll('.grid-item'));
    } else if (images.value) {
        masonry = new Masonry(images.value, {
            columnWidth: '.grid-sizer',
            itemSelector: '.grid-item',
            percentPosition: true,
            stagger: 0
        });
        window.masonry = masonry;
    }
    const imgs = images.value.querySelectorAll('img');
    const imgLoadPromises = [];
    for (let img of imgs) {
        if (!img.complete) {
            imgLoadPromises.push(new Promise(res => {
                img.onload = () => res();
            }));
        }
    }
    Promise.all(imgLoadPromises).then(() => {
        masonry.once('layoutComplete', () => {
            stopLoading();
        });
        masonry.layout();
    })
});

const gridBreakpoints = {
    // From 0-800 use 1 column
    800: 1,
    // From 800-1200 use 2 columns
    1200: 2,
    // From 1200-1600 use 3 columns
    1600: 3,
    // Above 1600 use 4 columns
};
const getGridWidth = () => {
    return Math.ceil(window.innerWidth / numCols.value);
}
const getNumCols = () => {
    const vw = window.innerWidth;
    let cols = 1;
    if (vw >= 800 && vw < 1200) {
        cols = 2;
    } else if (vw >= 1200 && vw < 1600) {
        cols = 3;
    } else if (vw >= 1600) {
        cols = 4;
    }
    return cols
}
const numCols = ref(getNumCols());
const gridWidth = ref(getGridWidth());
const resizeDB = debounce(() => {
    numCols.value = getNumCols();
    gridWidth.value = getGridWidth();
}, 200);
window.addEventListener('resize', resizeDB);

const items = computed(() => {
    const rtn = [];
    for (let item of album.value?.items) {
        let _item = {
            order: item.order,
            gridSize: 1,
        }
        if (item.hasOwnProperty('paths')) {
            let srcset = [];
            let sizes = [];
            let max_width = item.max_width;
            if (max_width > item.max_height) {
                _item['gridSize'] = 2;
            }
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
            const getClosestWidth = (toWidth) => {
                let width = max_width;
                for (let w in item.paths) {
                    const wNum = parseInt(w);
                    if (item.paths.hasOwnProperty(w) && wNum >= toWidth) {
                        if (wNum < width) {
                            width = wNum;
                        }
                    }
                }
                return width;
            }
            let prev = 0;
            for (let w in gridBreakpoints) {
                if (gridBreakpoints.hasOwnProperty(w)) {
                    const cols = gridBreakpoints[w];
                    const colWidth = gridWidth.value;
                    let itemCols = _item.gridSize;
                    if (cols < itemCols) {
                        itemCols = cols;
                    }
                    let p = '';
                    if (prev) {
                        p = `min-width: ${prev+1}px and `
                    }
                    // The _slot_ part of the `sizes` simply needs to know how
                    // big the image will display
                    const minImgWidth = colWidth * itemCols;
                    sizes.push(`(${p}max-width: ${w}px) ${minImgWidth}px`);
                    prev = parseInt(w);
                }
            }
            // The _slot_ part of the `sizes` simply needs to know how
            // big the image will display
            let maxImgWidth = gridWidth.value * _item.gridSize;
            if (numCols.value < _item.gridSize) {
                maxImgWidth = gridWidth.value & numCols.value;
            }
            sizes.push(`(min-width: ${prev}px) ${maxImgWidth}px`);

            _item['type'] = 'image';
            _item['srcset'] = srcset.join(',');
            _item['sizes'] = sizes.join(',');
            _item['src'] = item.paths[getClosestWidth(maxImgWidth)];
        } else if (item.hasOwnProperty('text')) {
            _item['type'] = 'text';
            _item['text'] = item.text;
        }
        rtn.push(_item);
    }
    return rtn.toSorted((a,b) => a.order - b.order);
});

let viewContainer;
function toggleGigante(ev, img) {
    const i = ev.target;
    const rect = i.getClientRects().item(0);
    const viewContTainer = document.getElementById('view-container-container');
    viewContainer = document.getElementById('view-container');
    viewContainer.addEventListener('click', () => closeGigante(i, img), {
        once: true,
    });
    const iClone = i.cloneNode();
    iClone.setAttribute('sizes', '100vw'); // Make sure the browser loads the proper image
    iClone.classList.remove('w-100');
    viewContainer.appendChild(iClone);
    viewContTainer.classList.remove('d-none');
    viewContainer.style.top = rect.top+'px';
    viewContainer.style.left = rect.left+'px';
    viewContainer.style.width = rect.width+'px';
    viewContainer.style.height = rect.height+'px';
    setTimeout(() => {
        viewContTainer.classList.add('blur-bg');
        viewContainer.style.top = 0;
        viewContainer.style.left = 0;
        viewContainer.style.width = '100vw';
        viewContainer.style.height = '100vh';
    }, 50);
}

function closeGigante(i, img) {
    const rect = i.getClientRects().item(0);
    viewContainer = document.getElementById('view-container');
    viewContainer.style.top = rect.top+'px';
    viewContainer.style.left = rect.left+'px';
    viewContainer.style.width = rect.width+'px';
    viewContainer.style.height = rect.height+'px';
    viewContainer.parentElement.classList.remove('blur-bg');
    setTimeout(() => {
        viewContainer.removeChild(viewContainer.children.item(0));
        viewContainer.parentElement.classList.add('d-none');
    }, 500);
}
</script>

<template>
    <div v-if="album" class="images" ref="images">
        <div class="grid-sizer"></div>
        <div v-for="item of items" class="grid-item image-container"
             :class="[`grid-item--width-${item.gridSize}`]">
            <img v-if="item.type =='image'" :srcset="item.srcset" :sizes="item.sizes" :src="item.src"
                 class="w-100 opacity-0" @click="toggleGigante($event, item)">
            <pre v-else-if="item.type =='text'">{{ item.text }}</pre>
        </div>
    </div>
    <div class="d-flex position-fixed justify-content-center loading-spinner" ref="load-spinner">
        <div class="spinner-border"></div>
    </div>
    <div id="view-container-container" class="d-none">
        <div id="view-container"></div>
    </div>
</template>

<style>
@media screen and (min-width: 800px) {
    .image-container {
        transition: 0.2s filter linear;
        filter: contrast(85%) grayscale(20%);
    }

    .image-container:hover {
        opacity: 1;
        filter: contrast(100%) grayscale(0%);
    }
}
.image-container.gigante {
    width: 100vw;
    opacity: 1;
    filter: grayscale(0);
}

.image-container > img:not(.opacity-0), .loading-spinner:not(.opacity-0) {
    transition: opacity .3s;
}

.grid-sizer, .grid-item {
    width: 100vw;
}
@media screen and (min-width: 800px) {
    .grid-sizer, .grid-item {
        width: 50vw;
    }
    .grid-item--width-2 {
        width: 100vw;
    }
}
@media screen and (min-width: 1200px) {
    .grid-sizer, .grid-item {
        width: 33.3vw;
    }
    .grid-item--width-2 {
        width: 66.6vw;
    }
}
@media screen and (min-width: 1600px) {
    .grid-sizer, .grid-item {
        width: 25vw;
    }
    .grid-item--width-2 {
        width: 50vw;
    }
}

#view-container-container {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    transition: backdrop-filter 500ms;
    backdrop-filter: blur(0px) grayscale(0%);
}
#view-container-container.blur-bg {
    backdrop-filter: blur(7px) grayscale(80%);
}

#view-container {
    position: fixed;
    transition: all 500ms;
    display: flex;
    justify-content: center;
    align-items: center;
}

#view-container > img {
    object-fit: contain;
    max-width: 100%;
    max-height: 100%;
}

.loading-spinner {
    width: 100vw;
    left: 0;
    top: 10vh;
}
</style>