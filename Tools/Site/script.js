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

// Function to show the news

// Define the API endpoint
const apiUrl = 'https://newsapi.org/v2/everything?q=tesla&from=2024-07-29&sortBy=publishedAt&apiKey=5a278471f75e44d6ae67ec2d31aa9b52';

// Function to call the API
async function fetchData() {
    try {
        const response = await fetch(apiUrl); // Make the API request
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json(); // Parse the JSON data
        data.articles.forEach(article => {
            // Create a new element for each article
            const articleElement = document.createElement('div');
            articleElement.classList.add('article');
            articleElement.innerHTML = `
                <h2>${article.title}</h2>
                <p>${article.description}</p>
                <a href="${article.url}" target="_blank">Read more</a>
                //date
                <p>${article.publishedAt}</p>
            `;
            draggableWindow.appendChild(articleElement);
        });
        console.log(data); // Log the data to the console
    } catch (error) {
        console.error('There has been a problem with your fetch operation:', error);
    }
}

// Call the function to fetch data
fetchData();


function ShowNews() {
    fetchData();
}