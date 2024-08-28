// script.js

// Function to make an element draggable
function makeDraggable(element) {
    let isMouseDown = false;
    let offset = { x: 0, y: 0 };

    const onMouseDown = (e) => {
        isMouseDown = true;
        offset.x = e.clientX - element.getBoundingClientRect().left;
        offset.y = e.clientY - element.getBoundingClientRect().top;
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    };

    const onMouseMove = (e) => {
        if (!isMouseDown) return;
        const x = e.clientX - offset.x;
        const y = e.clientY - offset.y;
        element.style.left = `${x}px`;
        element.style.top = `${y}px`;
    };

    const onMouseUp = () => {
        isMouseDown = false;
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
    };

    element.addEventListener('mousedown', onMouseDown);
}

// Make the window draggable
const draggableWindow = document.getElementById('draggableWindow');
makeDraggable(draggableWindow);
