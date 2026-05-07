export const debounce = function(callback, delay) {
    let timer;
    return function() {
        clearTimeout(timer);
        timer = setTimeout(() => callback(), delay);
    }
};