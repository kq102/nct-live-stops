document.addEventListener('DOMContentLoaded', function() {
    // USING MAPBOX 3
    const map = new mapboxgl.Map({
        container: 'map',
        center: [-1.1581, 52.9548],
        zoom: 9.7,
        style: 'mapbox://styles/mapbox/standard',
        accessToken: 'pk.eyJ1Ijoia3lsZW5jdHgiLCJhIjoiY21keWNuMW1sMDBrdDJscjExdHFsZzRxbiJ9.Hi9vxYCi1hph6lJMwSfZ2g'
    });

    map.addControl(new mapboxgl.NavigationControl());
    map.addControl(new mapboxgl.FullscreenControl());
    map.addControl(new mapboxgl.GeolocateControl({
            positionOptions: {enableHighAccuracy: true},
            // When active the map will receive updates to the device's location as it changes.
            trackUserLocation: true,
            // arrow next to the location dot to indicate direction of travel.
            showUserHeading: true
        })
    );

    // SET THE LIGHTING TO THE NICE DAWN PRESET. day is default, dusk, night also available
    map.on('style.load', () => {
        map.setConfigProperty('basemap', 'lightPreset', 'dawn');
    });

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

    window.hideSidebar = function() 
    {
        var sidebar = document.getElementById('sidebar');
        selectedStopId=null;
        clearInterval(updateInterval)
        // Fade out
        sidebar.style.opacity = '0';
        setTimeout(() => {
            sidebar.style.display = 'none';
        }, 200);
        sidebarContent.innerHTML = '<div class="loading">Loading times...</div>';
    }

    // Function to load all stops
    function loadAllStops() {
        
        // ESTABLISH TOP LEVEL OF THE STOPGEOJSON
        let stopGeoJson = {"type": "FeatureCollection", "features": []}

        fetch('/get_all_stops')
            .then(response => response.json())
            .then(stops => {
                stops.forEach(stop => {
                    // PARSING THE LATITUDE AND LONGITUD, CONVERT TO FLOAT
                    let coordinate = [parseFloat(stop.lon), parseFloat(stop.lat)];

                    // REMOVEING THE LAT & LON FROM PROPERTIES BEFORE CREATING THE FEATURE
                    let properties = stop;
                    delete properties.lon;
                    delete properties.lat;

                    // CREATING A GEOJSON FEATURE FROM THE STOPS DATA
                    let feature = {"type": "Feature", "geometry":{"type": "Point", "coordinates": coordinate}, "properties": properties}

                    // PUSH THE FEATURE TO THE LIST
                    stopGeoJson.features.push(feature)

                    // const marker = L.circleMarker([stop.lat, stop.lon], {
                    //     radius: 6,
                    //     color: '#333',
                    //     fillColor: '#fff',
                    //     fillOpacity: 1,
                    //     weight: 2
                    // }).addTo(map);

                    // marker.bindTooltip(stop.stop_name, {
                    //     permanent: false,
                    //     direction: 'top'
                    // });

                    // marker.on('click', () => selectStop(stop.stop_code, stop.stop_name));
                    // marker.on('click', () => showSidebar())
                    // stopMarkers[stop.stop_code] = marker;
                    
                });
                // ADD GEOJSON OF STOPS AS A DATA SOURCE
                map.addSource('stopGeoJson',{'type': 'geojson', 'generateId': true, 'data': stopGeoJson})
                // ADD ALL STOPS TO A LAYER
                map.addLayer({
                    'id': 'stopGeoJson',
                    'type': 'circle',
                    'source': 'stopGeoJson',
                    'paint': {
                        'circle-color': '#3144ac',
                        'circle-radius': 6,
                        'circle-stroke-width': 2,
                        'circle-stroke-color': '#ffffff'
                    }
                });

                // NEW POPUP OBJECT, disable default close functionalities
                const popup = new mapboxgl.Popup({
                    closeButton: false,
                    closeOnClick: false
                });

                // ON MOUSE HOVER, SHOW POPUP
                map.addInteraction('stopGeoJson-mouseenter-interaction', {
                    type: 'mouseenter',
                    target: { layerId: 'stopGeoJson' },
                    handler: (e) => {
                        map.getCanvas().style.cursor = 'pointer';

                        // COPY COORDINATES FROM THE ICON
                        const coordinates = e.feature.geometry.coordinates.slice();
                        const description = e.feature.properties.stop_name;

                        // SET COORDINATES AND HTML OF THE POPUP AND ADD IT TO THE MAP
                        popup.setLngLat(coordinates).setHTML(description).addTo(map);
                    }
                });

                // ON MOUSE HOVER LEAVE, CLOSE POPUP
                map.addInteraction('stopGeoJson-mouseleave-interaction', {
                    type: 'mouseleave',
                    target: { layerId: 'stopGeoJson' },
                    handler: () => {
                        map.getCanvas().style.cursor = '';
                        popup.remove();
                    }
                });

                // ON ICON CLICK, OPEN SIDEBAR
                map.addInteraction('stopGeoJson-click',{
                    type: 'click',
                    target: {layerId: 'stopGeoJson'},
                    handler: (e) => {
                        selectStop(e.feature.properties.stop_code, e.feature.properties.stop_name);
                        showSidebar()
                    }
                })
                map.addInteraction('map-click', {
                    type: 'click',
                    handler: () => {
                        hideSidebar();
                    }
                });
            });
    }

    function selectStop(stopId, stopName) {
        if (selectedStopId != stopId){
            sidebarContent.innerHTML = '<div class="loading">Loading times...</div>';
        }
        selectedStopId = stopId;
        
        // Clear previous update interval
        if (updateInterval) {
            clearInterval(updateInterval);
        }

        // // Reset marker styles
        // Object.values(stopMarkers).forEach(marker => {
        //     marker.setStyle({
        //         color: '#333',
        //         fillColor: '#fff'
        //     });
        // });

        // // Highlight selected stop
        // if (stopMarkers[selectedStopId]) {
        //     stopMarkers[selectedStopId].setStyle({
        //         color: '#007bff',
        //         fillColor: '#007bff'
        //     });
        // }

        updateStopTimes(selectedStopId, stopName);
        
        // Start regular updates
        updateInterval = setInterval(() => {
            updateStopTimes(selectedStopId, stopName);
        }, 15000);
    }

    function updateStopTimes(stopId, stopName) {

        // Only show loading on first load
        if ((!document.querySelector('.stopComparison'))) {
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
            const [route, dest, timeValue] = time.split('~');
            return `
                <div class="timeEntry">
                    <div class=timeEntry-left>
                        <div class="route">${route}</div>
                        <div class="destination">${dest}</div>
                    </div>
                    <div class="time">${timeValue}</div> 
                </div>
            `;
        }).join('');
    }

    // Search functionality
    const searchInput = document.getElementById('stopSearchInput');
    const searchButton = document.getElementById('searchStopButton');

    function searchStop() {
        const searchValue = searchInput.value.trim().toLowerCase();

        const source = map.getSource('stopGeoJson');
        const features = source._data.features;

        const matching = features.find(feature =>
            feature.properties.stop_name.toLowerCase().includes(searchValue)
        );

        if (matching){
            map.flyTo({
                center: matching.geometry.coordinates,
                zoom: 17,
                essential: true
            });
        }
    }

    searchButton.addEventListener('click', searchStop);
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') searchStop();
    });

    loadAllStops();
    
});