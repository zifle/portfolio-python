import "./gigante.css";

let viewContainer;
export function toggleGigante(ev, img) {
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

    requestAnimationFrame(() => {
        viewContTainer.classList.add('blur-bg');
        viewContainer.style.top = 0;
        viewContainer.style.left = 0;
        viewContainer.style.width = '100vw';
        viewContainer.style.height = '100vh';
    });
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