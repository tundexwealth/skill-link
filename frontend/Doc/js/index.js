fetch(`${window.CONFIG.API_URL}/api/v1/top_six_services`)
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById("popular-services-container");

        if (!container) {
            return;
        }

        const services = Array.isArray(data.top_six_services) ? data.top_six_services : [];

        container.innerHTML = services
            .map(service => `
                <div class="col-lg-4 col-md-6 col-sm-6">
                    <div class="single-location mb-30">

                        <div class="location-img">
                            <img src="${resolveImageUrl(service.image_url)}" alt="${service.name}" width="360" height="286">
                        </div>

                        <div class="location-details">
                            <p>${service.name}</p>

                            <a href="listing.html?category=${service.id}" class="location-btn">
                                ${service.service_count}
                                <i class="ti-plus"></i>
                                Providers
                            </a>
                        </div>

                    </div>
                </div>
            `)
            .join("");

    })
    .catch(error => {
        console.error(error);
    });


function renderStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    let starsHtml = '';

    for (let i = 0; i < fullStars; i++) {
        starsHtml += '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://w3.org"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="#ff3d1c" stroke="#ff3d1c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    }

    if (hasHalfStar && fullStars < 5) {
        starsHtml += '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://w3.org"><defs><linearGradient id="halfStarGrad"><stop offset="50%" stop-color="#ff3d1c"/><stop offset="50%" stop-color="#E0E0E0"/></linearGradient></defs><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="url(#halfStarGrad)" stroke="#ff3d1c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    }

    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    for (let i = 0; i < emptyStars; i++) {
        starsHtml += '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://w3.org"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="none" stroke="#E0E0E0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    }

    return `<span class="rating-stars">${starsHtml}</span>`;
}

function getRatingHtml(service) {
    const avgRating = Number(service.average_rating ?? service.avg_rating ?? 0);
    const totalRatings = Number(service.total_ratings ?? service.rating_count ?? 0);
    const normalizedRating = Number.isFinite(avgRating) ? avgRating : 0;
    const normalizedCount = Number.isFinite(totalRatings) ? totalRatings : 0;

    const starsHtml = renderStars(normalizedRating);
    const ratingText = normalizedRating > 0 || normalizedCount > 0
        ? `${normalizedRating.toFixed(1)} · ${normalizedCount} ${normalizedCount === 1 ? "review" : "reviews"}`
        : "No ratings yet";

    return `
        <div class="rating-badge ${normalizedRating > 0 || normalizedCount > 0 ? "" : "no-rating"}">
            ${starsHtml}
            <span class="rating-text">${ratingText}</span>
        </div>
    `;
}
function getRatingHtmltwo(service) {
    const avgRating = Number(service.average_rating ?? service.avg_rating ?? 0);
    const totalRatings = Number(service.total_ratings ?? service.rating_count ?? 0);
    const normalizedRating = Number.isFinite(avgRating) ? avgRating : 0;
    const normalizedCount = Number.isFinite(totalRatings) ? totalRatings : 0;

    const starsHtml = renderStars(normalizedRating);
    const ratingText = normalizedRating > 0 || normalizedCount > 0
        ? `${normalizedRating.toFixed(1)} · ${normalizedCount} ${normalizedCount === 1 ? "review" : "reviews"}`
        : "No ratings yet";

    return starsHtml;
}

function resolveImageUrl(imageUrl) {
    if (!imageUrl) {
        return "assets/img/gallery/list1.png";
    }

    if (/^(https?:)?\/\//i.test(imageUrl)) {
        return imageUrl;
    }

    if (imageUrl.startsWith("/")) {
        return imageUrl;
    }

    return imageUrl;
}

function isValidCoordinate(value) {
    return Number.isFinite(Number(value));
}

function renderProviderMap(latitude, longitude, address) {
    const mapContainer = document.getElementById("map");
    const messageContainer = document.getElementById("map-message");

    if (messageContainer) {
        messageContainer.style.display = "none";
        messageContainer.textContent = "";
    }

    if (!mapContainer || typeof window.L === "undefined") {
        return;
    }

    const lat = Number(latitude);
    const lng = Number(longitude);

    if (!isValidCoordinate(lat) || !isValidCoordinate(lng)) {
        showProviderMapUnavailable();
        return;
    }

    mapContainer.innerHTML = "";

    const map = window.L.map(mapContainer, {
        center: [lat, lng],
        zoom: 13,
        scrollWheelZoom: false
    });

    window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);

    window.L.marker([lat, lng]).addTo(map).bindPopup(address || "Provider location").openPopup();
}

function showProviderMapUnavailable() {
    const mapContainer = document.getElementById("map");
    const messageContainer = document.getElementById("map-message");

    if (mapContainer) {
        mapContainer.innerHTML = "";
    }

    if (messageContainer) {
        messageContainer.style.display = "block";
        messageContainer.textContent = "Location data is unavailable for this provider.";
    }
}

function truncateText(text, maxCharacters = 75) {
    if (!text) {
        return "Service available";
    }

    const normalizedText = String(text).trim();

    if (normalizedText.length <= maxCharacters) {
        return normalizedText;
    }

    const truncated = normalizedText.slice(0, maxCharacters);
    const lastSpace = truncated.lastIndexOf(" ");

    return `${lastSpace > 0 ? truncated.slice(0, lastSpace) : truncated}...`;
}

function cleanServiceTitle(title) {
    if (!title) {
        return "Service";
    }

    return String(title)
        .trim()
        .replace(/\s+placeholder\s+service\.?$/i, "")
        .trim();
}

function loadCategories(type) {
    fetch(`${window.CONFIG.API_URL}/api/v1/categories?type=${type}`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById("categories-container");

            container.innerHTML = data.categories
                .map(category => `
                <div class="col-lg-3 col-md-6 col-sm-6">
                    <div class="single-cat text-center mb-50">
                        <div class="cat-icon">
                            <img
                                src="${resolveImageUrl(category.image_url)}"
                                alt="${category.name}"
                                style="width:70px;height:70px;object-fit:cover;border-radius:50%;"
                            >
                        </div>
                        <div class="cat-cap">
                            <h5>
                                <a href="listing.html?category=${category.id}">
                                    ${category.name}
                                </a>
                            </h5>
                            <p>${category.description}</p>
                            <a href="listing.html?category=${category.id}">
                                View Details
                            </a>
                        </div>
                    </div>
                </div>
            `)
                .join("");
        })
        .catch(error => {
            console.error("Error fetching categories:", error);
        });
    if (type == "None") {
        document.getElementById('description').textContent = `All Categories`;
        document.getElementById('category_header').textContent = `All Categories`;
    }
    else if (type == "home") {
        document.getElementById('description').textContent = `Home & Maintenance`;
        document.getElementById('category_header').textContent = `Home & Maintenance Categories`;
    }
    else if (type == "education") {
        document.getElementById('description').textContent = `Education & Learning`;
        document.getElementById('category_header').textContent = `Education & Learning Categories`;
    }
    else if (type == "professional") {
        document.getElementById('description').textContent = `Professional Services`;
        document.getElementById('category_header').textContent = `Professional Services Categories`;
    }
    else if (type == "creative") {
        document.getElementById('description').textContent = `Creative & Digital Services`;
        document.getElementById('category_header').textContent = `Creative & Digital Services Categories`;
    }
}

let currentPage = 1;
const ITEMS_PER_PAGE = 6;

function getPageSize() {
    const pageSize = Number(window.pageSize);
    return Number.isFinite(pageSize) && pageSize > 0 ? pageSize : ITEMS_PER_PAGE;
}

function setCurrentPage(page) {
    const totalServices = Number(window.totalServiceCount || 0);
    const totalPages = Math.max(1, Math.ceil(totalServices / getPageSize()));
    currentPage = Math.min(Math.max(1, page), totalPages);
}

function renderPagination(totalServices) {
    const paginationContainer = document.getElementById("pagination-controls");

    if (!paginationContainer) {
        return;
    }

    const pageSize = getPageSize();
    const totalPages = Math.max(1, Math.ceil(totalServices / pageSize));
    const currentPage = Math.min(Math.max(1, window.currentPage || 1), totalPages);
    const pages = [];
    const windowSize = 4;

    const paginationWrapper = paginationContainer.closest('.pagination-area');
    if (paginationWrapper) {
        paginationWrapper.style.display = totalPages <= 1 ? 'none' : '';
    }

    if (totalPages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }

    const addPage = page => {
        pages.push(`
            <li class="page-item ${page === currentPage ? "active" : ""}">
                <a class="page-link" href="#" data-page="${page}">${String(page).padStart(2, "0")}</a>
            </li>
        `);
    };

    const addEllipsis = () => {
        pages.push(`
            <li class="page-item disabled">
                <span class="page-link">&hellip;</span>
            </li>
        `);
    };

    let startPage = currentPage;
    if (currentPage > totalPages - windowSize + 1) {
        startPage = totalPages - windowSize + 1;
    }
    startPage = Math.max(1, startPage);
    const endPage = Math.min(totalPages, startPage + windowSize - 1);

    if (startPage > 2) {
        addPage(1);
        addEllipsis();
    }

    for (let page = startPage; page <= endPage; page += 1) {
        addPage(page);
    }

    if (endPage < totalPages - 1) {
        addEllipsis();
        addPage(totalPages);
    } else if (endPage === totalPages - 1) {
        addPage(totalPages);
    }

    paginationContainer.innerHTML = pages.join("");

    paginationContainer.querySelectorAll("[data-page]").forEach(link => {
        link.addEventListener("click", event => {
            event.preventDefault();
            const page = Number(link.getAttribute("data-page"));
            if (Number.isFinite(page) && page !== currentPage) {
                loadServices(window.currentCategoryId || "all", page, pageSize, window.currentSearchFilters);
            }
        });
    });
}

function renderServices(services) {
    const container = document.getElementById("services-container");

    if (!container) {
        console.error("services-container not found");
        return;
    }

    const safeServices = Array.isArray(services) ? services : [];
    const totalServices = Number(window.totalServiceCount || safeServices.length);
    const totalPages = Math.max(1, Math.ceil(totalServices / (window.pageSize || ITEMS_PER_PAGE)));
    const safePage = Math.min(Math.max(1, window.currentPage || 1), totalPages);
    window.currentPage = safePage;
    const pageServices = safeServices;

    container.innerHTML = pageServices.length
        ? pageServices.map(service => `
            <div class="col-lg-6">
                <div class="single-listing mb-30">
                    <div class="list-img">
                        <img src="${resolveImageUrl(service.image_url) || 'assets/img/gallery/list1.png'}" alt="${service.title || 'Service'}" width="360" height="251">
                    </div>
                    <div class="list-caption">
                        <h3 style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
                            <a href="listing_details.html?provider=${service.provider_id}">${cleanServiceTitle(service.title) || 'Service'} ${service.provider_verified ? '<svg xmlns="http://w3.org" viewBox="0 0 24 24" width="24" height="24" fill="#008000"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-1.9 14.7L5.6 12.2l1.4-1.4 3.1 3.1 7-7 1.4 1.4-8.4 8.4z"/></svg>' : ''}</a>
                        </h3>
                        ${getRatingHtmltwo(service)}
                        <p class="service-description">${truncateText(service.description)}</p>
                        <div class="list-footer">
                            <ul>
                                <li>☎️ ${service.provider_phone || 'Contact for info'}</li>
                                <li>${service.location_name || 'Available now'}</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `).join("")
        : '<div class="col-12"><p>No services available.</p></div>';

    const countElement = document.querySelector(".count span");
    if (countElement) {
        countElement.textContent = `${totalServices} Listings are available`;
    }

    renderPagination(totalServices);
}

function normalizeSearchText(value) {
    return String(value || "")
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, " ")
        .replace(/\s+/g, " ")
        .trim();
}

function getExpandedSearchTerms(queryText) {
    const normalizedQuery = normalizeSearchText(queryText);

    if (!normalizedQuery) {
        return [];
    }

    const synonymMap = {
        electrician: ["electrician", "electician", "electrical", "electric", "wiring", "power"],
        electrical: ["electrician", "electician", "electrical", "electric", "wiring", "power"],
        plumber: ["plumber", "plumbing", "pipe", "water", "drain", "repair"],
        plumbing: ["plumber", "plumbing", "pipe", "water", "drain", "repair"],
        cleaning: ["cleaning", "clean", "housekeeping", "janitor", "washing"],
        hair: ["hair", "salon", "styling", "barber", "beauty", "stylist"],
        salon: ["hair", "salon", "styling", "barber", "beauty", "stylist"],
        tutor: ["tutor", "teach", "teaching", "lesson", "education", "class", "coach"],
        tutoring: ["tutor", "teach", "teaching", "lesson", "education", "class", "coach"],
        repair: ["repair", "fix", "maintenance", "service", "handyman"],
        maintenance: ["repair", "fix", "maintenance", "service", "handyman"],
        photography: ["photography", "photo", "camera", "videography", "shoot"],
        design: ["design", "designer", "graphic", "creative", "visual"],
        event: ["event", "planner", "party", "celebration"],
        food: ["food", "catering", "restaurant", "meal"],
        security: ["security", "guard", "protection", "safe"],
        car: ["car", "automobile", "garage", "mechanic", "repair"],
        laptop: ["laptop", "computer", "tech", "repair"],
        phone: ["phone", "mobile", "device", "repair"]
    };

    const terms = normalizedQuery.split(/\s+/).filter(Boolean);

    return [...new Set(terms.flatMap(term => [term, ...(synonymMap[term] || [])]))];
}

function serviceMatchesQuery(service, queryText) {
    const expandedTerms = getExpandedSearchTerms(queryText);

    if (!expandedTerms.length) {
        return true;
    }

    const searchableText = normalizeSearchText([
        service.title,
        service.description,
        service.provider_name,
        service.provider_business_name,
        service.category_name,
        service.business_name,
        service.location_name,
        service.location_city,
        service.location_state,
        service.location_address
    ].join(" "));

    return expandedTerms.some(term => searchableText.includes(term));
}

function filterServicesByQuery(services, queryText, locationText = "") {
    const normalizedQuery = normalizeSearchText(queryText);
    const normalizedLocation = normalizeSearchText(locationText);

    if (!normalizedQuery && !normalizedLocation) {
        return services;
    }

    const matchedServices = services.filter(service => {
        const matchesQuery = !normalizedQuery || serviceMatchesQuery(service, queryText);
        const matchesLocation = !normalizedLocation || [
            service.location_name,
            service.location_city,
            service.location_state,
            service.location_address
        ].some(value => normalizeSearchText(value).includes(normalizedLocation));
        return matchesQuery && matchesLocation;
    });

    if (matchedServices.length) {
        return matchedServices;
    }

    return services;
}

async function loadServicesForFeaturedCategory(type, queryText = "") {
    try {
        let services = [];
        let searchFilters = null;

        if (queryText) {
            searchFilters = { query: queryText };
        }

        if (!type || type === "all") {
            const params = new URLSearchParams({ category_id: "all", page: "1", page_size: "100" });
            if (searchFilters?.query) {
                params.set("query", searchFilters.query);
            }
            const response = await fetch(`${window.CONFIG.API_URL}/api/v1/categories/services?${params.toString()}`);
            const data = await response.json();
            services = Array.isArray(data.services) ? data.services : [];
        } else {
            const response = await fetch(`${window.CONFIG.API_URL}/api/v1/categories?type=${encodeURIComponent(type)}`);
            const data = await response.json();
            const categories = Array.isArray(data.categories) ? data.categories : [];

            const serviceResponses = await Promise.all(
                categories.map(category => {
                    const params = new URLSearchParams({ category_id: String(category.id), page: "1", page_size: "100" });
                    if (searchFilters?.query) {
                        params.set("query", searchFilters.query);
                    }
                    return fetch(`${window.CONFIG.API_URL}/api/v1/categories/services?${params.toString()}`)
                        .then(response => response.json())
                        .then(data => Array.isArray(data.services) ? data.services : []);
                })
            );

            services = serviceResponses.flat();
        }

        window.baseServices = services;
        const filteredServices = queryText ? filterServicesByQuery(services, queryText) : services;
        window.currentServices = filteredServices;
        setCurrentPage(1);
        setPriceSliderRange(services);
        renderServices(filteredServices);
    } catch (error) {
        console.error("Error loading featured category services:", error);
        renderServices([]);
    }
}

function applyListingFilters() {
    const query = (document.getElementById("advanced-search")?.value || document.getElementById("quick-search")?.value || "").trim();
    const location = (document.getElementById("advanced-location")?.value || "").trim();
    const normalizedQuery = normalizeSearchText(query);
    const normalizedLocation = normalizeSearchText(location);

    const rangeFrom = Number(document.querySelector(".js-input-from")?.value || 0);
    const rangeTo = Number(document.querySelector(".js-input-to")?.value || Number.MAX_SAFE_INTEGER);

    if (normalizedQuery || normalizedLocation) {
        const searchFilters = { query, location };
        window.currentSearchFilters = searchFilters;
        loadServices(
            window.currentCategoryId || "all",
            1,
            getPageSize(),
            searchFilters
        );
        return;
    }

    window.currentSearchFilters = null;
    window.searchMode = false;

    const baseServices = Array.isArray(window.baseServices) ? window.baseServices : [];

    const filteredServices = baseServices.filter(service => {
        const matchesPrice = Number(service.price || 0) >= rangeFrom && Number(service.price || 0) <= rangeTo;
        return matchesPrice;
    });

    window.currentServices = filteredServices;
    setCurrentPage(1);
    renderServices(filteredServices);
}

function populateFilterDropdowns(categories) {
    const categorySelects = [
        document.getElementById("quick-category"),
        document.getElementById("advanced-category")
    ].filter(Boolean);

    const locationInput = document.getElementById("advanced-location");

    categorySelects.forEach(select => {
        const currentValue = select.value || "";
        const options = ['<option value="">Choose categories</option>']
            .concat(categories.map(category => `<option value="${category.id}">${category.name}</option>`));
        select.innerHTML = options.join("");
        select.value = currentValue && categories.some(category => String(category.id) === String(currentValue)) ? currentValue : "";
    });

    if (locationInput) {
        const currentLocation = locationInput.value || "";
        locationInput.value = currentLocation;
    }
}

function loadCategoryOptions() {
    fetch(`${window.CONFIG.API_URL}/api/v1/categories?type=None`)
        .then(response => response.json())
        .then(data => {
            const categories = Array.isArray(data.categories) ? data.categories : [];
            populateFilterDropdowns(categories);
        })
        .catch(error => {
            console.error("Error fetching categories for filters:", error);
        });
}

function setPriceSliderRange(services) {
    const prices = (services || []).map(service => Number(service.price || 0)).filter(price => !Number.isNaN(price));
    const maxPrice = prices.length ? Math.max(...prices) : 1000;
    const roundedMax = Math.ceil(maxPrice / 1000) * 1000 || 1000;

    const slider = document.querySelector(".js-range-slider");
    const priceFrom = document.querySelector(".js-input-from");
    const priceTo = document.querySelector(".js-input-to");

    if (slider && window.jQuery && window.jQuery.fn && window.jQuery.fn.ionRangeSlider) {
        const instance = window.jQuery(slider).data("ionRangeSlider");
        if (instance) {
            instance.update({ min: 0, max: roundedMax, from: 0, to: roundedMax });
        }
    }

    if (priceFrom) priceFrom.value = 0;
    if (priceTo) priceTo.value = roundedMax;
}

function loadServices(categoryId, page = 1, pageSize = 6, searchFilters = null) {
    window.currentCategoryId = categoryId;
    window.currentSearchFilters = searchFilters;
    window.searchMode = Boolean(searchFilters && (searchFilters.query || searchFilters.location));

    const params = new URLSearchParams({
        category_id: categoryId,
        page: page.toString(),
        page_size: pageSize.toString(),
    });

    if (window.searchMode) {
        if (searchFilters.query) {
            params.set("query", searchFilters.query);
        }
        if (searchFilters.location) {
            params.set("location", searchFilters.location);
        }
    }

    fetch(`${window.CONFIG.API_URL}/api/v1/categories/services?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            const services = Array.isArray(data.services) ? data.services : [];
            window.baseServices = services;
            window.totalServiceCount = Number(data.total || services.length);
            window.currentPage = Number(data.page || page);
            window.pageSize = Number(data.page_size || pageSize);

            if (!Number.isFinite(window.pageSize) || window.pageSize <= 0) {
                window.pageSize = ITEMS_PER_PAGE;
            }

            setCurrentPage(window.currentPage);
            setPriceSliderRange(services);

            window.currentServices = services;
            renderServices(services);
        })
        .catch(error => {
            console.error("Error fetching services:", error);
        });
}

function configureListingFilters() {
    const quickSearchBtn = document.getElementById("quick-search-button");
    const quickSearchInput = document.getElementById("quick-search");
    const advancedSearchInput = document.getElementById("advanced-search");
    const advancedLocation = document.getElementById("advanced-location");
    const quickCategory = document.getElementById("quick-category");
    const advancedCategory = document.getElementById("advanced-category");

    loadCategoryOptions();

    quickSearchBtn?.addEventListener("click", () => {
        applyListingFilters();
    });

    quickSearchInput?.addEventListener("keydown", event => {
        if (event.key === "Enter") {
            event.preventDefault();
            applyListingFilters();
        }
    });

    advancedSearchInput?.addEventListener("input", applyListingFilters);
    advancedLocation?.addEventListener("change", applyListingFilters);
    advancedCategory?.addEventListener("change", applyListingFilters);
    quickCategory?.addEventListener("change", () => {
        const selectedCategory = quickCategory.value;
        if (selectedCategory) {
            window.location.href = `listing.html?category=${selectedCategory}`;
        }
    });

    const priceFrom = document.querySelector(".js-input-from");
    const priceTo = document.querySelector(".js-input-to");
    priceFrom?.addEventListener("input", applyListingFilters);
    priceTo?.addEventListener("input", applyListingFilters);

    const resetButton = document.getElementById("reset-filters");
    resetButton?.addEventListener("click", () => {
        if (advancedSearchInput) advancedSearchInput.value = "";
        if (advancedLocation) advancedLocation.value = "";
        if (quickSearchInput) quickSearchInput.value = "";

        window.currentSearchFilters = null;
        window.searchMode = false;

        const baseServices = Array.isArray(window.baseServices) ? window.baseServices : [];
        window.currentServices = baseServices;
        setCurrentPage(1);
        setPriceSliderRange(baseServices);
        renderServices(baseServices);
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", configureListingFilters);
} else {
    configureListingFilters();
}

async function loadTotalListings(category_id) {
    if (!category_id) {
        return;
    }

    fetch(`${window.CONFIG.API_URL}/api/v1/total_listings?category_id=${category_id}`)
        .then(response => response.json())
        .then(data => {
            const countElement = document.querySelector(".count span");
            if (countElement) {
                countElement.textContent = `${data.total_listings} Listings are available`;
            }
        })
        .catch(error => {
            console.error("Error fetching total listings:", error);
        });
}

async function loadProviderDetails(provider_id) {
    const container = document.getElementById("provider-details");

    if (!container) {
        console.error("provider-details container not found");
        return;
    }

    try {
        const response = await fetch(
            `${window.CONFIG.API_URL}/api/v1/provider_services?provider_id=${provider_id}`
        );

        if (!response.ok) {
            throw new Error("Failed to load provider details.");
        }

        const data = await response.json();
        const services = data.services || [];

        if (services.length === 0) {
            container.innerHTML = `
                <p>No services found for this provider.</p>
            `;
            return;
        }

        const provider = services[0];
        const heroBanner = document.getElementById("hero-banner");
        const serviceDescription = document.getElementById("service_description");

        const locations = [...new Set(services.map(service => service.location_name))];
        const mainAddress = locations[0] || "Provider location";
        const otherLocations = locations.slice(1, 3);

        const locationPoint = services.find(s => Number.isFinite(Number(s.latitude)) && Number.isFinite(Number(s.longitude))) || provider;
        const providerLatitude = locationPoint.latitude != null ? Number(locationPoint.latitude) : null;
        const providerLongitude = locationPoint.longitude != null ? Number(locationPoint.longitude) : null;
        const mapData = {
            latitude: providerLatitude,
            longitude: providerLongitude,
            address: mainAddress
        };

        if (Number.isFinite(mapData.latitude) && Number.isFinite(mapData.longitude)) {
            renderProviderMap(mapData.latitude, mapData.longitude, mapData.address);
        } else {
            showProviderMapUnavailable();
        }

        if (serviceDescription) {
            serviceDescription.textContent = cleanServiceTitle(provider.title) || "Service Title unavailable.";
        }

        if (heroBanner) {
            heroBanner.style.backgroundImage = `url(${provider.image_url || 'assets/img/gallery/list1.png'})`;
        }

        // Fallback description
        const aboutProvider =
            data.about ||
            `${provider.title} provides professional services with quality, reliability, and attention to detail. Our experienced team is available for different events and personal needs.`;

        // Services
        const serviceHTML = services
            .map(service => `
            <div class="service-card">
                <div class="service-card__content">
                    <div class="service-card__title-row">
                        <h5>${service.title || "Service"}</h5>
                        <span class="service-card__price">₦${Number(service.price).toLocaleString()}</span>
                    </div>

                    <p class="service-card__description">
                        ${service.description || "Service details coming soon."}
                    </p>

                    <div class="service-card__meta">
                        <span class="service-card__pill">📍 ${service.location_name || "Location available"}</span>
                    </div>
                </div>
            </div>
    `)
            .join("");

        // Other locations
        const locationHTML =
            otherLocations.length > 0
                ? `
                    <div class="provider-section">
                        <h4 class="mt-40">Other Locations</h4>

                        <p>
                            We also provide our services in:
                        </p>

                        <div class="location-list">
                            ${otherLocations
                    .map(
                        location => `
                                <div class="location-pill">📍 ${location}</div>
                            `
                    )
                    .join("")}
                        </div>
                    </div>
                `
                : "";
        // const commented_code = '<h3 class="mb-20">
        //         ${provider.title}
        //     </h3>

        //     <img
        //         src="${provider.image_url}"
        //         class="img-fluid mb-30"
        //         alt="${provider.title}"
        //     ></img>'

        container.innerHTML = `
            <div class="provider-details-shell">
                <div class="provider-details-card">
                    <div class="provider-rating-summary">
                        ${getRatingHtml(provider)}
                    </div>

                    <div class="provider-contact-card">
                        <p class="mb-20">
                            <strong>Phone:</strong>
                            ${provider.provider_phone || 'Not listed'}
                        </p>

                        ${provider.provider_website ? `
                        <p class="mb-20">
                            <strong>Website:</strong>
                            <a href="https://${provider.provider_website}" target="_blank" rel="noopener noreferrer">${provider.provider_website}</a>
                        </p>
                        ` : ''}

                        ${provider.provider_linkedin_url ? `
                        <p class="mb-20">
                            <strong>LinkedIn:</strong>
                            <a href="https://${provider.provider_linkedin_url}" target="_blank" rel="noopener noreferrer">${provider.provider_linkedin_url}</a>
                        </p>
                        ` : ''}

                        <p class="mb-20">
                            <strong>Status:</strong>
                            ${provider.provider_verified ? '<span class="badge badge-success" style="background:#28a745;color:#fff;">Verified Provider</span>' : '<span class="badge badge-secondary">Not verified</span>'}
                        </p>

                        ${provider.provider_is_imported ? `
                        <p class="mb-20">
                            <strong>Source:</strong>
                            Imported${provider.provider_imported_from ? ` from ${provider.provider_imported_from}` : ''}
                        </p>
                        ` : ''}

                        <p class="mb-20">
                            <strong>Address:</strong>
                            ${mainAddress}
                        </p>
                    </div>

                    <div class="provider-section">
                        <h3 class="mb-20">
                            About this Provider
                        </h3>

                        <p class="mb-30">
                            ${aboutProvider}
                        </p>
                    </div>

                    <div class="provider-section">
                        <h3 class="mb-30">
                            Services Offered
                        </h3>

                        <div class="services-offered-grid">
                            ${serviceHTML}
                        </div>
                    </div>

                    ${locationHTML}

                    <div class="provider-section" style="text-align: center;" id="claim-action-container">
                        <!-- claim action inserted here -->
                    </div>

                    <div class="provider-section" style="text-align: center;">
                        <button class="rate-provider-btn" onclick="openRatingModal(${provider_id})">⭐ Rate This Provider</button>
                    </div>
                </div>
            </div>
        `;

        initializeClaimAction(provider_id, provider.provider_verified);

    } catch (error) {
        console.error(error);

        container.innerHTML = `
            <p>Unable to load provider information.</p>
        `;
    }
}

async function initializeClaimAction(providerId, providerVerified) {
    const container = document.getElementById('claim-action-container');
    if (!container) {
        return;
    }

    container.innerHTML = '';

    if (providerVerified) {
        container.innerHTML = '<p class="text-success">This business is already verified.</p>';
        return;
    }

    const showClaimButton = (label, disabled = false, extraHtml = '') => {
        container.innerHTML = `
            <button class="btn btn-primary" id="claim-provider-btn" ${disabled ? 'disabled' : ''}>${label}</button>
            ${extraHtml}
        `;
        const button = document.getElementById('claim-provider-btn');
        if (button && !disabled) {
            button.addEventListener('click', async () => {
                await submitClaimRequest(providerId);
            });
        }
    };

    try {
        const authCheck = await fetch(`${window.CONFIG.API_URL}/api/v1/auth-check`, {
            credentials: 'include',
        });
        const authData = await authCheck.json();

        if (!authCheck.ok || !authData.authenticated) {
            showClaimButton('Log in to claim this business');
            const button = document.getElementById('claim-provider-btn');
            if (button) {
                button.addEventListener('click', () => {
                    window.location.href = 'login.html';
                });
            }
            return;
        }

        const response = await fetch(`${window.CONFIG.API_URL}/api/v1/providers/${providerId}/claim-status`, {
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error('Unable to check claim status.');
        }

        const data = await response.json();

        if (data.status === 'pending') {
            container.innerHTML = '<button class="btn btn-secondary" disabled>Claim request pending</button>';
        } else if (data.status === 'approved') {
            container.innerHTML = '<button class="btn btn-success" disabled>Claim request approved</button>';
        } else if (data.status === 'rejected') {
            showClaimButton('Claim this business', false, '<p class="text-danger mt-3">Your previous claim request was rejected. You can try again.</p>');
        } else {
            showClaimButton('Claim this business');
        }
    } catch (error) {
        console.error('Claim status error:', error);
        showClaimButton('Claim this business');
    }
}

async function submitClaimRequest(providerId) {
    const button = document.getElementById('claim-provider-btn');
    if (button) {
        button.disabled = true;
        button.textContent = 'Submitting...';
    }

    try {
        const response = await fetch(`${window.CONFIG.API_URL}/api/v1/providers/${providerId}/claim`, {
            method: 'POST',
            credentials: 'include',
        });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to submit claim request.');
        }

        alert(data.message || 'Claim request submitted successfully.');
        initializeClaimAction(providerId, false);
    } catch (error) {
        console.error('Claim request error:', error);
        alert(error.message || 'Unable to submit claim request.');
        if (button) {
            button.disabled = false;
            button.textContent = 'Claim this business';
        }
    }
}

async function loadOtherProviders(provider_id) {
    fetch(`${window.CONFIG.API_URL}/api/v1/other_provider_services?provider_id=${provider_id}&page=1&page_size=3`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById("provider-services-list");

            if (!container) {
                console.error("provider-services-list not found");
                return;
            }

            const services = Array.isArray(data.services) ? data.services : [];
            const listingContainer =
                document.getElementById("provider-services-list");

            if (listingContainer) {

                if (services.length > 0) {

                    listingContainer.innerHTML = services.map(service => `

            <div class="col-lg-4 col-md-6">

                <div class="single-listing mb-30">

                    <div class="list-img">

                        <img
                            src="${service.image_url}"
                            alt="${service.title || 'Service'}"
                        >

                    </div>

                    <div class="list-caption">

                        ${getRatingHtmltwo(service)}

                        <h3>
                            <a href="listing_details.html?provider=${service.id}" || '#'}">${service.title || 'Unnamed Service'}</a>
                        </h3>

                        <p>
                            ${service.description || 'No description available.'}
                        </p>

                        <div class="list-footer">

                            <ul>

                                <li>
                                    ${service.provider_phone}
                                </li>

                                <li>
                                    ₦${Number(service.price).toLocaleString()}
                                </li>

                            </ul>

                        </div>

                    </div>

                </div>

            </div>

        `).join("");

                } else {

                    listingContainer.innerHTML = `

            <div class="col-12 text-center">

                <h4>No related services available yet.</h4>

                <p>
                    More services will be added in the future.
                </p>

            </div>

        `;

                }

            }
        })
}


window.checkAuthStatus = async function () {

    const loggedIn = document.getElementById("logged-in-content");
    const loggedOut = document.getElementById("logged-out-content");
    const loggedInWithProvider = document.getElementById("logged-in-with-provider-content");
    const adminLink = document.getElementById("admin-link");

    if (!loggedIn || !loggedOut || !loggedInWithProvider)
        return;

    loggedIn.style.display = "none";
    loggedOut.style.display = "none";
    loggedInWithProvider.style.display = "none";
    if (adminLink) adminLink.style.display = "none";

    try {

        const response = await fetch(
            `${window.CONFIG.API_URL}/api/v1/auth-check`,
            {
                credentials: "include"
            }
        );

        if (!response.ok)
            throw new Error("Auth check failed");

        const data = await response.json();

        if (!data.authenticated) {
            loggedOut.style.display = "";
            return;
        }

        loggedIn.style.display = "";
        loggedOut.style.display = "none";

    } catch (err) {

        console.error(err);
        loggedOut.style.display = "";
        return;

    }

    try {
        const response_two = await fetch(
            `${window.CONFIG.API_URL}/api/v1/auth/me`,
            {
                credentials: "include"
            }
        );

        if (!response_two.ok) {
            throw new Error("Auth user check failed");
        }

        const authUser = await response_two.json();
        if (adminLink) {
            adminLink.style.display = authUser.user && authUser.user.is_admin ? "" : "none";
        }

        const response_three = await fetch(
            `${window.CONFIG.API_URL}/api/v1/providers/me`,
            {
                credentials: "include"
            }
        );

        if (!response_three.ok) {
            throw new Error("Provider check failed");
        }

        const data_two = await response_three.json();

        if (data_two.provider === null) {
            loggedIn.style.display = "";
            loggedInWithProvider.style.display = "none";
        } else {
            loggedIn.style.display = "none";
            loggedInWithProvider.style.display = "";
        }

    } catch (err) {
        console.error(err);
        loggedIn.style.display = "";
        loggedInWithProvider.style.display = "none";
    }

};


// ============ RATING SYSTEM FUNCTIONS ============

let currentProviderId = null;
let selectedRating = 0;

async function openRatingModal(providerId) {
    try {
        const response = await fetch(`${window.CONFIG.API_URL}/api/v1/auth-check`, {
            credentials: 'include'
        });

        const data = await response.json();

        if (!response.ok || !data.authenticated) {
            alert('You must be logged in to rate a provider.');
            return;
        }
    } catch (error) {
        console.error('Auth check failed for rating modal:', error);
        alert('You must be logged in to rate a provider.');
        return;
    }

    currentProviderId = providerId;
    selectedRating = 0;

    // Reset claim action state if it exists
    const claimActionContainer = document.getElementById('claim-action-container');
    if (claimActionContainer) {
        claimActionContainer.innerHTML = '';
    }

    // Reset form
    document.getElementById('ratingComment').value = '';
    document.getElementById('selectedRating').textContent = '0';
    document.getElementById('submitRatingBtn').disabled = true;

    // Reset star selection
    document.querySelectorAll('.star-option').forEach(star => {
        star.classList.remove('selected');
    });

    // Show modal
    document.getElementById('ratingModal').classList.add('show');
}

function closeRatingModal() {
    document.getElementById('ratingModal').classList.remove('show');
    currentProviderId = null;
    selectedRating = 0;
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('ratingModal');
    if (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                closeRatingModal();
            }
        });
    }

    // Star picker functionality
    const starPicker = document.getElementById('starPicker');
    if (starPicker) {
        starPicker.addEventListener('click', function (e) {
            if (e.target.classList.contains('star-option')) {
                selectedRating = parseInt(e.target.dataset.rating);

                // Update visual selection
                document.querySelectorAll('.star-option').forEach((star, index) => {
                    if (index < selectedRating) {
                        star.classList.add('selected');
                    } else {
                        star.classList.remove('selected');
                    }
                });

                // Update text
                document.getElementById('selectedRating').textContent = selectedRating;

                // Enable submit button
                document.getElementById('submitRatingBtn').disabled = false;
            }
        });
    }
});

async function submitRating() {
    if (!currentProviderId || selectedRating === 0) {
        alert('Please select a rating.');
        return;
    }

    const comment = document.getElementById('ratingComment').value.trim();
    const submitBtn = document.getElementById('submitRatingBtn');

    // Disable button during submission
    submitBtn.disabled = true;
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Submitting...';

    try {
        const response = await fetch(`${window.CONFIG.API_URL}/api/v1/ratings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                provider_id: currentProviderId,
                score: selectedRating,
                comment: comment || null
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to submit rating.');
        }

        // Success
        alert('Thank you! Your rating has been submitted.');
        closeRatingModal();

        // Reload provider details to show updated rating
        const params = new URLSearchParams(window.location.search);
        const providerId = params.get('provider');
        if (providerId) {
            loadProviderDetails(providerId);
        }

    } catch (error) {
        console.error('Rating submission error:', error);
        alert('Error: ' + error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}
