document.addEventListener('DOMContentLoaded', () => {
    const draggableWindow = document.querySelector('.draggable');
    const header = draggableWindow.querySelector('.header');
    const closeButton = document.getElementById('close-button');

    let isDragging = false;
    let offsetX, offsetY;

    header.addEventListener('mousedown', (e) => {
        if (e.target !== closeButton) {
            isDragging = true;
            offsetX = e.clientX - draggableWindow.getBoundingClientRect().left;
            offsetY = e.clientY - draggableWindow.getBoundingClientRect().top;
        }
    });

    document.addEventListener('mousemove', (e) => {
        if (isDragging) {
            draggableWindow.style.left = `${e.clientX - offsetX}px`;
            draggableWindow.style.top = `${e.clientY - offsetY}px`;
        }
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
    });

    closeButton.addEventListener('click', () => {
        draggableWindow.style.display = 'none';
    });
});

        function adjustIframeSize() {
            const draggableElement = document.getElementById('draggable-element');
            const iframe = document.getElementById('bokeh-iframe');
            iframe.style.width = draggableElement.clientWidth + 'px';
            iframe.style.height = draggableElement.clientHeight + 'px';
        }

        // Adjust iframe size initially
        adjustIframeSize();

        // Adjust iframe size on window resize
        window.addEventListener('resize', adjustIframeSize);

        // Adjust iframe size when the draggable element is resized
        const observer = new ResizeObserver(adjustIframeSize);
        observer.observe(document.getElementById('draggable-element'));