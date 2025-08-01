document.addEventListener('DOMContentLoaded', function() {
    // Initialize map similar to vehicle map
    var map = L.map('map', {
        zoomControl: false
    }).setView([52.9548, -1.1581], 12);

    L.control.zoom({position:'topright'}).addTo(map);

    // Add tile layers
    var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    });

    var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles © Esri'
    });

    osm.addTo(map);

    var baseMaps = {
        "OpenStreetMapDefault": osm,
        "Satellite": satellite
    };

    L.control.layers(baseMaps, null, {position: 'topright'}).addTo(map);





    function formatTimes(times) {
        if (!times || times.length === 0) {
            return '<div class="timeEntry">No times available</div>';
        }

        return times.map(time => {
            const [route, dest, timeValue] = time.split('-');
            return `
                <div class="timeEntry">
                    ${route} to ${dest}: ${timeValue}
                </div>
            `;
        }).join('');
    }
    
});