mapboxgl.accessToken = mapboxAccessToken;

// Default view: entire world (same approach as Precip_web). center + zoom set the initial view.
// zoom 0 = whole world; center [0, 20] keeps the map well-framed.
var map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/satellite-v9',
  center: [0, 20],
  zoom: 0,
  minZoom: 0,
  maxZoom: 18,
  maxBounds: [[-180, -85], [180, 85]]
});

// Create a single popup instance to reuse for hover
var hoverPopup = new mapboxgl.Popup({
  closeButton: false,
  closeOnClick: false,
  offset: [0, -40] // Adjust offset to move the popup up or down (x, y)
});

// Track the active popup and timeout
let popupTimeout;

// Fetch volcano data from the API and add to the map
fetch('/api/volcanoes')
  .then(response => response.json())
  .then(data => {
    data.forEach(volcano => {
      // Create a wrapper div around the default marker
      var wrapperDiv = document.createElement('div');
      wrapperDiv.className = 'marker-wrapper';

      // Create a default marker
      var marker = new mapboxgl.Marker({
        color: '#f47321' // Replace with your desired hex color code
      })
        .setLngLat([volcano.longitude, volcano.latitude])
        .addTo(map);

      // Append the marker's element to the wrapper div
      wrapperDiv.appendChild(marker.getElement());

      // Add the wrapper div to the map
      map.getCanvasContainer().appendChild(wrapperDiv);

      // Add click event to open volcano detail page in a new tab
      wrapperDiv.addEventListener('click', () => {
        window.open(volcano.volcdef_link, '_blank');
      });

      // Add hover events to show the name of the volcano
      wrapperDiv.addEventListener('mouseenter', () => {
        clearTimeout(popupTimeout); // Clear any existing timeout
        hoverPopup
          .setLngLat([volcano.longitude, volcano.latitude])
          .setText(volcano.name)
          .addTo(map);
      });

      // Delay removing popup on mouse leave to prevent flickering
      wrapperDiv.addEventListener('mouseleave', () => {
        popupTimeout = setTimeout(() => {
          hoverPopup.remove();
        }, 50); // Adjust the delay as needed
      });

      // Add touch events to show the name of the volcano on mobile devices
      wrapperDiv.addEventListener('touchstart', () => {
        clearTimeout(popupTimeout); // Clear any existing timeout
        hoverPopup
          .setLngLat([volcano.longitude, volcano.latitude])
          .setText(volcano.name)
          .addTo(map);
      });

      // Remove popup on touchend (optional: you can adjust behavior as needed)
      wrapperDiv.addEventListener('touchend', () => {
        popupTimeout = setTimeout(() => {
          hoverPopup.remove();
        }, 2000); // Keep the popup visible for a while on touchend
      });
    });
  })
  .catch(error => {
    console.error('Error fetching volcano data:', error);
  });

// Add CSS styles (optional, adjust as needed)
var style = document.createElement('style');
style.type = 'text/css';
style.innerHTML = `
  .marker-wrapper {
    position: absolute;
    width: 30px; /* Adjust size as needed */
    height: 30px; /* Adjust size as needed */
    cursor: pointer; /* Change cursor on hover */
  }
`;
document.getElementsByTagName('head')[0].appendChild(style);
