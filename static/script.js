let minPrice = 0;
let maxPrice = 15000;
let minArea = 0;
let maxArea = 100;
let distance = 500;
let duration = 30;
function moveThumb(event, thumb, isMin, maxValue, step, displayElement, inputElement, unit) {
  const rect = sliderContainer.getBoundingClientRect();
  const offsetX = event.clientX - rect.left;
  const percentage = Math.min(Math.max(offsetX / rect.width * 100, 0), 100);
  const value = round(percentage * maxValue / 100, step);

  if (isMin) {
    minPrice = round(Math.min(Math.max(0, value), maxPrice - step), step);
    thumb.style.left = `${minPrice * 100 / maxValue}%`;
  } else {
    maxPrice = round(Math.max(Math.min(maxValue, value), minPrice + step), step);
    thumb.style.left = `${maxPrice * 100 / maxValue}%`;
  }

  displayElement.textContent = `${minPrice} - ${maxPrice} ${unit}`;
  inputElement.value = Math.round(isMin ? minPrice : maxPrice);
}

function moveSingleThumb(event, thumb, maxValue, step, displayElement, inputElement, unit) {
  const rect = sliderContainer.getBoundingClientRect();
  const offsetX = event.clientX - rect.left;
  const percentage = Math.min(Math.max(offsetX / rect.width * 100, 0), 100);
  const value = round(percentage * maxValue / 100, step);
  thumb.style.left = `${value * 100 / maxValue}%`;
  displayElement.textContent = `${value} ${unit}`;
  inputElement.value = Math.round(value);
}

document.addEventListener("DOMContentLoaded", function () {
  const sliderContainer = document.querySelector('.slider-container');
  const minPriceThumb = document.getElementById('minPriceThumb');
  const maxPriceThumb = document.getElementById('maxPriceThumb');
  const priceDispaly = document.getElementById('priceDisplay');
  const minPriceInput = document.getElementById('minPrice');
  const maxPriceInput = document.getElementById('maxPrice');

  const minAreaThumb = document.getElementById('minAreaThumb');
  const maxAreaThumb = document.getElementById('maxAreaThumb');
  const areaDisplay = document.getElementById('areaDisplay');
  const minAreaInput = document.getElementById('minArea');
  const maxAreaInput = document.getElementById('maxArea');

  const distanceThumb = document.getElementById('distanceThumb');
  const distanceDisplay = document.getElementById('distanceDisplay');
  const distanceInput = document.getElementById('distance');

  const durationThumb = document.getElementById('durationThumb');
  const durationDisplay = document.getElementById('durationDisplay');
  const durationInput = document.getElementById('duration');

  minPriceThumb.addEventListener('mousedown', () => {
    const onMouseMove = (event) => moveThumb(event, minPriceThumb, true , 50000, 100, priceDispaly, minPriceInput, '元');
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', () => {
      document.removeEventListener('mousemove', onMouseMove);
    }, { once: true });
  });

  maxPriceThumb.addEventListener('mousedown', () => {
    const onMouseMove = (event) => moveThumb(event, maxPriceThumb, false, 50000, 100, priceDispaly, maxPriceInput, '元');
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', () => {
      document.removeEventListener('mousemove', onMouseMove);
    }, { once: true });
  });

  minAreaThumb.addEventListener('mousedown', () => {
    const onMouseMove = (event) => moveThumb(event, minAreaThumb, true, 100, 1, areaDisplay, minAreaInput, '坪');
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', () => {
      document.removeEventListener('mousemove', onMouseMove);
    }, { once: true });
  });

  maxAreaThumb.addEventListener('mousedown', () => {
    const onMouseMove = (event) => moveThumb(event, maxAreaThumb, false, 100, 1, areaDisplay, maxAreaInput, '坪');
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', () => {
      document.removeEventListener('mousemove', onMouseMove);
    }, { once: true });
  });

  distanceThumb.addEventListener('mousedown', () => {
    const onMouseMove = (event) => moveSingleThumb(event, distanceThumb, 50000, 10, distanceDisplay, distanceInput, '公尺');
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', () => {
      document.removeEventListener('mousemove', onMouseMove);
    }, { once: true });
  });

  durationThumb.addEventListener('mousedown', () => {
    const onMouseMove = (event) => moveSingleThumb(event, durationThumb, 6000, 10, durationDisplay, durationInput, '秒');
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', () => {
      document.removeEventListener('mousemove', onMouseMove);
    }, { once: true });
  });
});


document.addEventListener("DOMContentLoaded", function () {
  const schoolFrom = document.getElementById("school-form");
  const searchForm = document.getElementById("search-form");
  const resultSection = document.getElementById("result-section");
  const resultList = document.getElementById("result-list");

  const roomTypeMap = {
    "suite": "套房",
    "room": "雅房",
  };
  const rentTypeMap = {
    "room_share": "房間分租",
    "whole": "整棟出租",
    "suite": "獨立套房",
    "unknown": "其他",
  };
  const houseTypeMap = {
    "apartment": "公寓",
    "townhouse": "透天",
    "condoninium": "華廈",
    "dormitory": "學舍",
    "building": "大樓",
  };
  const materialMap = {
    "cement": "水泥",
  };
  const genderMap = {
    "M": "男",
    "F": "女",
    "N/A": "不拘",
  };

  schoolFrom.addEventListener("submit", async function (e) {
    e.preventDefault();
    const formData = new FormData(schoolFrom);
    const target = formData.get("target");


    // 呼叫初次查詢 API
    const response = await fetch("/set_school", {
      method: "POST",
      body: formData
    });

    const results = await response.json();

    // 顯示搜尋表單與結果區塊
    searchForm.style.display = "block";
    resultSection.style.display = "block";

    updateResultList(results);
  });

  searchForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const formData = new FormData(searchForm);
    const response = await fetch("/search", {
      method: "POST",
      body: formData
    });
    const results = await response.json();
    updateResultList(results);
  });

  function updateResultList(results) {
    resultList.innerHTML = "";
    results.forEach(item => {

      const a = document.createElement("a");
      // Convert item.url to string
      if(typeof item.url !== "string") {
        item.url = String(item.url);
      }
      // 如果item.url 開頭是 http:// 或 https://，則直接使用該網址
      // 否則，將網址前面加上 https://house.nfu.edu.tw/NCKU + item.url
      a.href = item.url.startsWith("http://") || item.url.startsWith("https://") ? item.url : "https://house.nfu.edu.tw/NCKU" + item.url;
      a.target = "_blank";
      a.style.textDecoration = "none"; // 移除底線
      a.style.color = "inherit";       // 繼承文字顏色

      const li = document.createElement("li");
      li.style.border = "1px solid #ccc";
      li.style.padding = "10px";
      li.style.marginBottom = "10px";

      // 建立其餘資訊的顯示
      const info = document.createElement("div");
      info.className="result-info";
      info.innerHTML = `
      <div class="info-grid">
        <p><strong>房型：</strong>${houseTypeMap[item.house_type]}</p>
        <p><strong>租金範圍：</strong>${item.min_price} ~ ${item.max_price}</p>
        <p><strong>押金範圍：</strong>${item.min_deposit} ~ ${item.max_deposit}</p>
        <p><strong>房間類型：</strong>${roomTypeMap[item.room_type]}</p>
        <p><strong>租賃類型：</strong>${rentTypeMap[item.rent_type]}</p>
        <p><strong>坪數：</strong>${item.area}</p>
        <p><strong>距離：</strong>${item.distance} 公尺</p>
        <p><strong>預估行程時間：</strong>${item.travel_time} 秒</p>
        <p><strong>剩餘空房數量：</strong>${item.rest_room_num}</p>
        <p><strong>地址：</strong>${item.city}${item.town}${item.address}</p>
        <p><strong>性別限制：</strong>${genderMap[item.gender]}</p>
        <p><strong>電表：</strong>${item.ammeter ? "有" : "無"}</p>
        <p><strong>材質：</strong>${materialMap[item.material]}</p>
      </div>
      `;
      
      li.appendChild(info);
      a.appendChild(li);
      resultList.appendChild(a);
    });
  }
});
