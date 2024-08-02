document.addEventListener('DOMContentLoaded', function() {
    let slideIndex = 0;
    const slides = document.querySelectorAll('.slideshow img');
    
    function showSlides() {
        slides.forEach((slide) => {
            slide.style.opacity = '0';
        });

        slideIndex++;
        if (slideIndex > slides.length) { 
            slideIndex = 1; 
        }

        slides[slideIndex - 1].style.opacity = '1';
        setTimeout(showSlides, 3000); // Change image every 3 seconds
    }

    showSlides(); // Initialize slideshow

    window.showFlights = function() {
        fetch('/flights')
            .then(response => response.json())
            .then(data => {
                const flightContainer = document.getElementById('flight-container');
                flightContainer.innerHTML = '';
                data.forEach(flight => {
                    const div = document.createElement('div');
                    div.className = 'flight-details';
                    div.innerHTML = `
                        <h3>${flight.source} to ${flight.destination}</h3>
                        <p>Price: $${flight.price}</p>
                    `;
                    flightContainer.appendChild(div);
                });
                flightContainer.classList.remove('hidden');
            });
    };
});
