<script setup>
import {computed, onMounted, useTemplateRef} from "vue";

const {'items': album_items} = defineProps(['items'])
const emit = defineEmits(['albumItems', 'listItems']);

const itemsList = computed(() => {
    const final_items = [];
    let order = 0;
    for (let item of album_items) {
        order = order+1;

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
            _item['desc'] = item.description || 'Photo#'+item.id+' in order#'+order;
        } else if (item.hasOwnProperty('text')) {
            _item['type'] = 'text';
            _item['text'] = item.text;
        }
        final_items.push(_item);
    }
    emit('listItems', final_items);
    return final_items;
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

let dragging = null;
let draggingOrder = null;
let dropInOrder = null;
const sortableList = useTemplateRef('sortable');
onMounted(() => {
    sortableList.value.addEventListener('dragstart', e => {
        let itemElm = getDragAfterElement(e.target, sortableList);
        itemElm.classList.add('dragging');
        const itemId = parseInt(itemElm.dataset.id);
        dragging = itemsList.value.find(itm => itm.id === itemId);
        draggingOrder = dragging.order;
    });
    sortableList.value.addEventListener('dragend', e => {
        // Clean up temp dragging vars (this is called after `drop` event, so we're done handling it)
        let itemElm = e.target;
        itemElm.classList.remove('dragging');
        const elms = sortableList.value.querySelectorAll('[draggable=true]');
        for (let elm of elms) {
            elm.classList.remove('over', 'drop-right', 'drop-left');
        }
        dropInOrder = null;
        draggingOrder = null;
        dragging = null;
    });
    sortableList.value.addEventListener('drop', e => {
        e.preventDefault();
        if (dropInOrder === null || dropInOrder === draggingOrder || dropInOrder === draggingOrder+1) {
            // We skip handling the drop if we're dropping in either the same order, or +1.
            // +1 order is essentially the same, since it will be "before the next" or "after this"
            return;
        }

        const list = album_items;
        const listLen = list.length;
        const newList = [];
        const moveItem = list.find(itm => itm.id === dragging.id);
        for (let i=0; i<listLen; i++) {
            if (i+1 === dropInOrder) {
                newList.push(moveItem);
            } else if (i+1 === dragging.order) {
                continue;
            }
            newList.push(list[i]);
        }
        if (dropInOrder > listLen) {
            // Make sure we append the item, if it was placed last
            newList.push(moveItem);
        }
        let order = 0;
        for (let itm of newList) {
            itm.order = order = order+1;
        }
        emit('albumItems', newList);
    });
    sortableList.value.addEventListener('dragleave', () => {
        dropInOrder = null;
        const elms = sortableList.value.querySelectorAll('[draggable=true]');
        for (let elm of elms) {
            elm.classList.remove('over', 'drop-right', 'drop-left');
        }
    });
    sortableList.value.addEventListener('dragover', e => {
        e.preventDefault();
        const draggingOverItemElm = getDragAfterElement(e.target, sortableList.value);
        const elms = sortableList.value.querySelectorAll('[draggable=true]');
        for (let elm of elms) {
            elm.classList.remove('over', 'drop-right', 'drop-left');
        }
        dropInOrder = null;

        if (draggingOverItemElm) {
            const targetW = e.target.clientWidth;
            const targetCenter = targetW/3;
            const hoverX = e.offsetX;
            const hoverOrder = parseInt(draggingOverItemElm.dataset.order);
            let cls = ['over'];
            if (hoverX < targetCenter) {
                // Dropping before elm
                cls.push('drop-left');
                dropInOrder = hoverOrder;
            } else if (hoverX > targetCenter*2) {
                // Dropping after elm
                cls.push('drop-right');
                dropInOrder = hoverOrder+1;
            }

            draggingOverItemElm.classList.add(...cls);
        }
    });
});
function getDragAfterElement(target, container) {
    if (target === document.body) return null;
    if (target === container) {
        return null;
    }
    if (target.attributes['draggable']) {
        return target;
    }
    return getDragAfterElement(target.parentElement, container);
}

</script>

<template>
    <div class="row images" ref="sortable">
        <div v-for="itm of itemsList" class="col-lg-3 col-6 mb-3 has-hover-controls"
             draggable="true" :data-order="itm.order" :data-id="itm.id">
            <div class="hover-controls">
                <span class="badge text-bg-danger clickable" @click="removeItem(itm)">X</span>
            </div>

            <img loading="lazy" :srcset="itm.srcset" :sizes="itm.sizes" :src="itm.src"
                 class="image-preview" v-if="itm.type === 'image'" :alt="itm.desc">
            <pre v-else-if="itm.type === 'text'">{{ itm.text }}</pre>
        </div>
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

.over::after, .over::before {
    content: '';
    display: block;
    position: absolute;
    width: 33%;
    height: 100%;
    background-color: rgba(33,33,33,0.3);
    top: 0;
}
.over::before {
    left: 0;
}
.over::after {
    right: 0;
}
.over.drop-left::before {
    background-color: rgba(0,255,0,0.3);
}
.over.drop-right::after {
    background-color: rgba(0,255,0,0.3);
}

.uploading {
    bottom: 20px;
    right: 20px;
    padding: 10px 20px;
    background-color: var(--bs-body-bg);
    border: 2px solid var(--bs-border-color);
}
</style>