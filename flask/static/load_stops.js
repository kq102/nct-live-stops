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


    var stopMarkers = {};
    var selectedStopId = null;
    var updateInterval;

    function showSidebar()
    {
        var sidebar = document.getElementById('sidebar');


        sidebar.style.opacity = '0';
        sidebar.style.display = 'block';

        sidebar.offsetHeight;

        // Fade in
        sidebar.style.opacity = '1';
        sidebar.style.transition = 'opacity 0.2s ease-in-out';
    }

    // Function to load all stops
    function loadAllStops() {
        fetch('/get_all_stops')
            .then(response => response.json())
            .then(stops => {
                stops.forEach(stop => {
                    const marker = L.circleMarker([stop.lat, stop.lon], {
                        radius: 6,
                        color: '#333',
                        fillColor: '#fff',
                        fillOpacity: 1,
                        weight: 2
                    }).addTo(map);

                    marker.bindTooltip(stop.stop_name, {
                        permanent: false,
                        direction: 'top'
                    });

                    marker.on('click', () => selectStop(stop.stop_code, stop.stop_name));
                    marker.on('click', () => showSidebar())
                    stopMarkers[stop.stop_code] = marker;
                });
            });
    }

    function selectStop(stopId, stopName) {
        selectedStopId = stopId;
        
        // Clear previous update interval
        if (updateInterval) {
            clearInterval(updateInterval);
        }

        // Reset marker styles
        Object.values(stopMarkers).forEach(marker => {
            marker.setStyle({
                color: '#333',
                fillColor: '#fff'
            });
        });

        // Highlight selected stop
        if (stopMarkers[stopId]) {
            stopMarkers[stopId].setStyle({
                color: '#007bff',
                fillColor: '#007bff'
            });
        }

        updateStopTimes(stopId, stopName);
        
        // Start regular updates
        updateInterval = setInterval(() => {
            updateStopTimes(stopId, stopName);
        }, 15000);
    }

    function updateStopTimes(stopId, stopName) {

        // Only show loading on first load
        if (!document.querySelector('.stopComparison')) {
            sidebarContent.innerHTML = '<div class="loading">Loading times...</div>';
        }

        fetch(`/compare_stop_times/${stopId}`)
            .then(response => response.json())
            .then(data => {
                var newContent= `
                    <div class="stopComparison">
                        <div class="comparisonTitle">${stopName}, ${stopId}</div>
                        <div class="countdown-bar">
                            <div class="progress"></div>
                        </div>                        
                        <div class="updateTime">Last updated: ${new Date().toLocaleTimeString()}</div>
                        <div class="timeColumns">
                            <div class="timeColumn">
                                <div class="columnTitle">NCT website & app times</div>
                                ${formatTimes(data.nct_times)}
                            </div>
                            <div class="timeColumn">
                                <div class="columnTitle">Times on signs at stop</div>
                                ${formatTimes(data.council_times)}
                            </div>
                        </div>
                    </div>
                `;

                //  temporary container to hold the new content
                const temp = document.createElement('div');
                temp.innerHTML = newContent;
                
                // Get the existing stopComparison element
                const existing = document.querySelector('.stopComparison');
                
                if (existing) {
                    // Reset the animation by removing and re-adding the progress element
                    const oldProgress = existing.querySelector('.progress');
                    if (oldProgress) {
                        const newProgress = oldProgress.cloneNode(true);
                        oldProgress.parentNode.replaceChild(newProgress, oldProgress);
                    }                    
                    // update only changed content
                    existing.innerHTML = temp.firstElementChild.innerHTML;
                } else {
                    // First load - set entire content
                    sidebarContent.innerHTML = newContent;
                }

            })
            .catch(error => {
                console.error('Error fetching times:', error);
                // Only show error if there's no existing content
                if (!document.querySelector('.stopComparison')) {
                    sidebarContent.innerHTML = '<div class="loading">Error loading times</div>';
                }
            });
    }

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

    // Search functionality
    const searchInput = document.getElementById('stopSearchInput');
    const searchButton = document.getElementById('searchStopButton');

    function searchStop() {
        const searchValue = searchInput.value.trim().toLowerCase();
        
        for (const [stopId, marker] of Object.entries(stopMarkers)) {
            if (marker.getTooltip().getContent().toLowerCase().includes(searchValue)) {
                map.setView(marker.getLatLng(), 15);
                marker.openTooltip();
                break;
            }
        }
    }

    searchButton.addEventListener('click', searchStop);
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') searchStop();
    });

    loadAllStops();
    
});