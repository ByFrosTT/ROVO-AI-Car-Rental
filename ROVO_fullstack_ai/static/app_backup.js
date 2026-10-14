const $ = q => document.querySelector(q), $$ = q => [...document.querySelectorAll(q)];
let cars = [], saved = new Set(JSON.parse(localStorage.getItem("rovoSaved") || "[]")), currentCar = null;
let userLocation = JSON.parse(localStorage.getItem("rovoUserLocation") || "null");
const money = n => new Intl.NumberFormat("en-IN").format(n);
const DEFAULT_CAR_IMAGE =
    "/static/car_images/default-car.jpg";

function handleCarImageError(img) {

    img.onerror = null;

    img.src = DEFAULT_CAR_IMAGE;
}
function carImage(c) {

    // Owner uploaded vehicle photos
    if (c.images_json) {
        try {

            const images =
                typeof c.images_json === "string"
                    ? JSON.parse(c.images_json)
                    : c.images_json;

            if (Array.isArray(images) && images.length > 0) {
                return `/uploads/${images[0]}`;
            }

        } catch (error) {
            console.warn(
                "ROVO: Could not parse uploaded images:",
                error
            );
        }
    }

    // Build exact database name
    const carName = `${c.brand} ${c.model}`.trim();

    // Remote catalogue image
    if (
        typeof CAR_IMAGES_REMOTE !== "undefined" &&
        CAR_IMAGES_REMOTE[carName]
    ) {
        return CAR_IMAGES_REMOTE[carName];
    }

    // Local catalogue fallback
    const slug = carName
        .toLowerCase()
        .replace(/&/g, "and")
        .replace(/:/g, "")
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "");

    return `/static/car_images/${slug}.jpg`;
}

function toast(t){ const e=$("#toast"); e.textContent=t; e.classList.add("show"); setTimeout(()=>e.classList.remove("show"),2300); }
function setTheme(t){ let a=t==="system"?(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"):t; document.documentElement.dataset.theme=a; localStorage.setItem("rovoTheme",t); $("#theme").textContent=a==="dark"?"☀":"☾"; $("#themeSelect").value=t; }
setTheme(localStorage.getItem("rovoTheme")||"dark");
$("#theme").onclick=()=>setTheme(document.documentElement.dataset.theme==="dark"?"light":"dark");
$("#themeSelect").onchange=e=>setTheme(e.target.value);

function view(id){
  $$(".view").forEach(v=>v.classList.remove("active")); $("#"+id).classList.add("active"); scrollTo({top:0,behavior:"smooth"});
  if(id==="explore") loadCars(); if(id==="saved") renderSaved(); if(id==="bookings") loadBookings();
}
$$('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));

const rentals=[["◷","Hourly","2–12 hours for errands and city trips"],["▣","Daily","A day, weekend or multi-day rental"],["▤","Long-Term","Weekly and monthly rentals"],["⌁","Outstation","Intercity and highway travel"],["✈","Airport / Special","Airport pickups and events"]];
$("#rentalTypes").innerHTML=rentals.map((r,i)=>`<div class="rental-card ${i===0?"active":""}"><span>${r[0]}</span><b>${r[1]}</b><small>${r[2]}</small></div>`).join("");
$$('.rental-card').forEach(c=>c.onclick=()=>{$$('.rental-card').forEach(x=>x.classList.remove('active'));c.classList.add('active')});
$("#tripDate").value=new Date(Date.now()+86400000).toISOString().slice(0,10);
$("#findCars").onclick=()=>view("explore");

function locationQuery(){
  const o={};
  if(userLocation?.lat!=null && userLocation?.lng!=null){o.lat=userLocation.lat;o.lng=userLocation.lng;}
  if(userLocation?.label)o.user_location=userLocation.label;
  return o;
}
function updateLocationUI(){
  const label=userLocation?.label || userLocation?.nearest_hub || "Mumbai";
  $("#locationLabel").textContent=label;
  $("#tripLocation").value=label;
}
function openLocationModal(){
  $("#locationModal").classList.add("open");
  $("#manualLocationWrap").classList.add("hidden");
  $("#nearbyHubPreview").classList.add("hidden");
}
$("#editLocationTop").onclick=openLocationModal;
$("#closeLocationModal").onclick=()=>$("#locationModal").classList.remove("open");
$("#notNow").onclick=()=>$("#locationModal").classList.remove("open");
$("#manualLocation").onclick=()=>{$("#manualLocationWrap").classList.remove("hidden");$("#manualLocationInput").focus()};

async function saveResolvedLocation(loc, message="Location updated"){
  userLocation={label:loc.label||loc.nearest_hub||"Mumbai",lat:loc.lat??null,lng:loc.lng??null,nearest_hub:loc.nearest_hub||loc.label||null};
  localStorage.setItem("rovoUserLocation",JSON.stringify(userLocation)); updateLocationUI(); $("#locationModal").classList.remove("open"); toast(message);
  if($("#explore").classList.contains("active")) loadCars();
}
$("#allowLocation").onclick=()=>{
  if(!navigator.geolocation){toast("Geolocation is not supported in this browser");return;}
  $("#allowLocation").textContent="Finding your nearest pickup hubs…";
  navigator.geolocation.getCurrentPosition(async pos=>{
    const r=await fetch('/api/location/resolve',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({lat:pos.coords.latitude,lng:pos.coords.longitude})});
    const d=await r.json(); $("#allowLocation").textContent="⌖ Use my current location"; await saveResolvedLocation(d,`Using ${d.label} area • nearest hub ${d.distance_to_hub_km} km`);
  },()=>{$("#allowLocation").textContent="⌖ Use my current location";toast("Location permission was not available. Choose an area manually.");$("#manualLocationWrap").classList.remove("hidden")},{enableHighAccuracy:true,timeout:9000,maximumAge:300000});
};
let locationSearchTimer;
$("#manualLocationInput").oninput=e=>{
  clearTimeout(locationSearchTimer); const q=e.target.value.trim(); if(!q)return;
  locationSearchTimer=setTimeout(async()=>{const d=await fetch('/api/location/search?q='+encodeURIComponent(q)).then(r=>r.json());$("#locationSuggestions").innerHTML=d.map(x=>`<option value="${x.name}"></option>`).join("")},180);
};
$("#saveManual").onclick=async()=>{
  const q=$("#manualLocationInput").value.trim(); if(!q)return;
  const d=await fetch('/api/location/search?q='+encodeURIComponent(q)).then(r=>r.json());
  if(d.length){await saveResolvedLocation({label:d[0].name,lat:d[0].lat,lng:d[0].lng,nearest_hub:d[0].name},`Location changed to ${d[0].name}`)}
  else {await saveResolvedLocation({label:q,lat:null,lng:null,nearest_hub:null},"Location saved. Precise distance is unavailable for this custom area.")}
};
if(userLocation){updateLocationUI()}else{setTimeout(openLocationModal,500)}

async function loadCars(){
  const p=new URLSearchParams({q:$("#search").value,category:$("#category").value,fuel:$("#fuel").value,transmission:$("#transmission").value,seats:$("#seats").value,max_price:$("#maxPrice").value,location:$("#filterLocation").value,limit:240,...locationQuery()});
  cars=await fetch('/api/cars?'+p).then(r=>r.json()); $("#count").textContent=cars.length; renderCars(cars);
}
function carImage(c){ return c.images?.length?`<img src="/uploads/${encodeURIComponent(c.images[0])}" alt="${c.brand} ${c.model}">`:`<div class="mini-car"></div>`; }
function card(c) {

    const dist = c.distance_km != null
        ? `<span class="tag distance">⌖ ${c.distance_km} km • ${c.nearest_pickup}</span>`
        : `<span class="tag">${c.nearest_pickup || c.location}</span>`;

    return `
        <article class="car-card">

            <div class="car-img">

                <img
                    src="${carImage(c)}"
                    alt="${c.brand} ${c.model}"
                    loading="lazy"
                    onerror="this.onerror=null; this.src='/static/car_images/default-car.jpg';"
                >

                <button
                    class="save image-save"
                    data-save="${c.id}"
                    aria-label="Save ${c.brand} ${c.model}"
                >
                    ${saved.has(c.id) ? "♥" : "♡"}
                </button>

                <span class="image-year">
                    ${c.year}
                </span>

            </div>

            <div class="car-body">

                <div class="car-top">
                    <b>${c.brand} ${c.model}</b>
                    <span class="rating">★ ${c.rating}</span>
                </div>

                <div class="specs">
                    <span>${c.seats} seats</span>
                    <span>${c.fuel}</span>
                    <span>${c.transmission}</span>
                </div>

                <div class="tags">
                    <span class="tag">${c.category}</span>
                    ${dist}
                </div>

                <div class="price-row">

                    <strong>
                        ₹${money(c.price)}
                        <small>/day</small>
                    </strong>

                    <button
                        class="link"
                        data-car="${c.id}"
                    >
                        View car
                    </button>

                </div>

            </div>

        </article>
    `;
}
function wire(){
  $$('[data-car]').forEach(b=>b.onclick=()=>openCar(+b.dataset.car));
  $$('[data-save]').forEach(b=>b.onclick=()=>{const id=+b.dataset.save;saved.has(id)?saved.delete(id):saved.add(id);localStorage.setItem('rovoSaved',JSON.stringify([...saved]));if($("#saved").classList.contains("active"))renderSaved();else loadCars()});
}
function renderCars(list){$("#carGrid").innerHTML=list.map(card).join("")||`<div class="card empty-state">No cars match those filters.</div>`;wire()}
['category','fuel','transmission','seats','filterLocation'].forEach(id=>$("#"+id).onchange=loadCars);$("#doSearch").onclick=loadCars;$("#maxPrice").oninput=e=>{$("#maxPriceText").textContent='₹'+money(e.target.value);loadCars()};

async function openCar(id){
  const p=new URLSearchParams(locationQuery()); currentCar=await fetch('/api/cars/'+id+'?'+p).then(r=>r.json()); const c=currentCar;
  const dist=c.distance_km!=null?`<p class="near-line">⌖ Nearest pickup: <b>${c.nearest_pickup}</b> • ${c.distance_km} km from your selected location</p>`:'';
  $("#modalBody").innerHTML=`<div class="detail"><div class="detail-visual">${carImage(c)}</div><div class="detail-copy"><span class="eyebrow">${c.category.toUpperCase()} • ${c.year}</span><h2>${c.brand} ${c.model}</h2><p>★ ${c.rating} • ${c.trips} trips</p><p>${c.fuel} • ${c.transmission} • ${c.seats} seats • ${c.bags} bags</p>${dist}<h3>₹${money(c.price)} / day</h3><h4>Pickup locations</h4><div class="locs">${c.locations.map(x=>`<div class="loc">⌖ ${x}</div>`).join('')}</div><button id="bookCar" class="btn primary">Book now</button></div></div>`;
  $("#modal").classList.add('open');$("#bookCar").onclick=()=>booking(c);
}
$("#closeModal").onclick=()=>$("#modal").classList.remove('open');
function booking(c){
  $("#modalBody").innerHTML=`<span class="eyebrow">BOOKING</span><h2>${c.brand} ${c.model}</h2><div class="booking-form"><div class="summary"><p>${c.fuel} • ${c.transmission} • ${c.seats} seats</p><p>From ₹${money(c.price)} / day</p><label>Driver name<input id="driverName"></label><label>Driving licence<input id="licence"></label><label>Start date<input id="startDate" type="date" value="${$("#tripDate").value}"></label><label>Days<input id="days" type="number" min="1" value="2"></label><label>Pickup location<select id="pickup">${c.locations.map(x=>`<option ${x===c.nearest_pickup?'selected':''}>${x}</option>`).join('')}</select></label></div><div class="summary"><h3>Transparent pricing</h3><p>Rental is calculated from the selected duration. Taxes and platform fee are shown before confirmation.</p><button id="confirmBook" class="btn primary">Confirm booking</button></div></div>`;
  $("#confirmBook").onclick=async()=>{const body={car_id:c.id,driver_name:$("#driverName").value,licence:$("#licence").value,start_date:$("#startDate").value,duration_days:+$("#days").value,pickup_location:$("#pickup").value};const r=await fetch('/api/bookings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const d=await r.json();if(!r.ok)return toast(d.error||'Booking failed');$("#modal").classList.remove('open');toast(`Booked ${d.code}`);view('bookings')};
}
async function loadBookings(){const b=await fetch('/api/bookings').then(r=>r.json());$("#bookingList").innerHTML=b.length?b.map(x=>`<div class="booking card"><div><b>${x.brand} ${x.model}</b><small>${x.start_date} • ${x.pickup_location}<br>${x.code} • ₹${money(x.total)}</small></div><span class="status">${x.status}</span></div>`).join(''):`<div class="card empty-state">No bookings yet.</div>`}
async function renderSaved(){const p=new URLSearchParams({limit:240,...locationQuery()});const all=await fetch('/api/cars?'+p).then(r=>r.json());const list=all.filter(c=>saved.has(c.id));$("#savedGrid").innerHTML=list.length?list.map(card).join(''):`<div class="card empty-state">No saved cars yet.</div>`;wire()}

$("#hostForm").onsubmit=async e=>{e.preventDefault();const fd=new FormData(e.target);const r=await fetch('/api/host/list-car',{method:'POST',body:fd});const d=await r.json();if(!r.ok)return toast(d.error||'Could not submit');toast(d.message);view('explore')};
$("#photos").onchange=e=>{const p=$("#photoPreview");p.innerHTML='';[...e.target.files].slice(0,8).forEach(f=>{const img=document.createElement('img');img.src=URL.createObjectURL(f);p.appendChild(img)})};

function openAi(){$("#aiPanel").classList.add('open');if(!$("#aiMessages").children.length)addAI('Tell me the trip naturally. I can use hills/ghats, fuel efficiency, passenger count, budget, luggage and your actual pickup distance. Try: “fuel-efficient automatic for hilly roads, close to me.”')}
$("#aiFab").onclick=openAi;$("#mobileAi").onclick=openAi;$("#askAiHero").onclick=openAi;$("#closeAi").onclick=()=>$("#aiPanel").classList.remove('open');
function addUser(t){const d=document.createElement('div');d.className='msg user';d.textContent=t;$("#aiMessages").appendChild(d)}
function addAI(t,c=[]){
  const d=document.createElement('div'); d.className='msg ai';
  const sliderId='slider_'+Date.now()+'_'+Math.floor(Math.random()*9999);
  const cards=c.length?`<div class="ai-slider-wrap"><button class="slider-nav prev" data-slide-prev="${sliderId}">‹</button><div class="ai-rec-slider" id="${sliderId}">${c.map(x=>`<article class="rec-card"><div class="rec-match">${x.match}% match</div><b>${x.brand} ${x.model}</b><small>₹${money(x.price)}/day • ${x.fuel} • ${x.transmission}</small><small class="rec-location">⌖ ${x.location}${x.distance_km!=null?` • ${x.distance_km} km`:''}</small><p>${x.why}</p><button class="btn secondary rec-view" data-ai-car="${x.id}">View car</button></article>`).join('')}</div><button class="slider-nav next" data-slide-next="${sliderId}">›</button></div>`:'';
  d.innerHTML=`<div>${t}</div>${cards}`; $("#aiMessages").appendChild(d); $("#aiMessages").scrollTop=$("#aiMessages").scrollHeight;
  d.querySelectorAll('[data-ai-car]').forEach(b=>b.onclick=()=>openCar(+b.dataset.aiCar));
  d.querySelectorAll('[data-slide-prev]').forEach(b=>b.onclick=()=>document.getElementById(b.dataset.slidePrev).scrollBy({left:-260,behavior:'smooth'}));
  d.querySelectorAll('[data-slide-next]').forEach(b=>b.onclick=()=>document.getElementById(b.dataset.slideNext).scrollBy({left:260,behavior:'smooth'}));
}
async function sendAI(t){
  addUser(t); const d=await fetch('/api/ai/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t,current_car_id:currentCar?.id,user_location:userLocation||{}})}).then(r=>r.json()); addAI(d.answer,d.cars||[]);
}
$("#aiForm").onsubmit=e=>{e.preventDefault();const t=$("#aiInput").value.trim();if(!t)return;$("#aiInput").value='';sendAI(t)};
$$('.quick button').forEach(b=>b.onclick=()=>sendAI(b.textContent));
async function resetAI(){await fetch('/api/ai/reset',{method:'POST'});$("#aiMessages").innerHTML='';currentCar=null;toast('ROVO AI trip memory cleared');openAi()}
$("#newAiChat").onclick=resetAI;$("#resetAiProfile").onclick=resetAI;

async function logout(){
  await fetch('/api/logout',{method:'POST'}); localStorage.removeItem('rovoSaved');localStorage.removeItem('rovoUserLocation');saved=new Set();userLocation=null;currentCar=null;$("#aiMessages").innerHTML='';updateLocationUI();toast('Logged out');view('home');setTimeout(openLocationModal,600);
}
$("#logoutTop").onclick=logout;$("#logoutProfile").onclick=logout;
