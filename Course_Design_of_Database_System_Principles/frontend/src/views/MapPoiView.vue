<template>
  <div class="map-poi-view">
    <div class="map-container">
      <!-- 地图 -->
      <div class="map" ref="mapRef">
        <div class="map-overlay">
          <div class="search-box">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索地点或POI"
              :prefix-icon="Search"
              @keyup.enter="handleSearch"
            />
            <el-button type="primary" @click="handleSearch" :icon="Search">
              搜索
            </el-button>
          </div>
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="info-panel">


        <!-- 👇 已点击景点记录 -->
        <div class="panel-header">
          <h3>已点击景点记录</h3>
          <el-button size="small" @click="clearClickedList">清空</el-button>
        </div>

        <el-table
          :data="clickedScenicList"
          size="small"
          height="100%"
          border
        >
          <el-table-column prop="poi_name" label="景点名" width="80" />
          <el-table-column prop="poi_type" label="类型" width="50" />
          <el-table-column prop="address" label="地址" width="70" />
          <el-table-column prop="occupancy_rate" label="占用率" width="70">
            <template #default="{ row }">
              {{ row.occupancy_rate ? (row.occupancy_rate > 1 ? row.occupancy_rate.toFixed(2) + '%' : (row.occupancy_rate * 100).toFixed(2) + '%') : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="weather_alert_status" label="天气预警" width="100">
            <template #default="{ row }">
              <el-tag
                :type="row.weather_alert_status === '受影响' ? 'danger' : 'success'"
                size="small"
              >
                {{ row.weather_alert_status || '无预警' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, onUnmounted, shallowRef } from 'vue'
import { Search, Location, Coordinate, Star } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// --- Map SDK 相关变量 ---
const mapRef = ref(null)          // 地图容器的DOM引用
const mapInstance = shallowRef(null) // 高德地图实例，使用 shallowRef 避免不必要的响应式开销
const currentMarkers = ref([])    // 存储地图上的所有 POI 标记实例
const infoWindow = shallowRef(null) // 信息窗体实例

// --- 搜索相关 ---
const searchKeyword = ref('')
const searchSuggestions = ref([]) // 搜索建议
const showSuggestions = ref(false)
const placeSearch = shallowRef(null) // AMap.PlaceSearch 实例

// --- POI数据 ---
const nearbyPois = ref([]) // 存储从后端或地图SDK获取的附近POI数据
const selectedPoi = ref(null)
const poisLoading = ref(false) // 附近POI列表加载状态
const clickedScenicList = ref([]) // 存储已点击的景点记录

// --- 地图状态 (由SDK管理，但可读取) ---
const currentMapCenter = ref({ lat: 31.2304, lng: 121.4737 }) // 地图中心点
const currentMapBounds = ref(null) // 地图当前可视区域边界

// --- 辅助函数 ---
const getPoiTypeTag = (type) => {
  const typeMap = {
    '景区': 'success', '酒店': 'warning', '餐厅': 'danger',
    '商场': 'info', '交通': 'primary', '娱乐': '', // 添加更多类型
    // 兼容高德地图的类型
    '餐饮服务': 'danger', '住宿服务': 'warning', '风景名胜': 'success',
    '购物服务': 'info', '交通设施服务': 'primary', '生活服务': '',
  }
  return typeMap[type] || ''
}

// --- 地图初始化与管理 ---
const initMap = () => {
  if (window.AMap && mapRef.value) {
    mapInstance.value = new window.AMap.Map(mapRef.value, {
      zoom: 14,                                     // 初始缩放级别
      center: [currentMapCenter.value.lng, currentMapCenter.value.lat], // 初始中心点
      viewMode: '3D'                                // 使用 3D 视图
    });

    // 创建 PlaceSearch 实例用于 POI 搜索
    window.AMap.plugin(['AMap.PlaceSearch', 'AMap.Geocoder'], () => {
      placeSearch.value = new window.AMap.PlaceSearch({
        pageSize: 10,  // 每页结果数
        pageIndex: 1,  // 页码
        city: '上海市', // 限定搜索城市
        map: mapInstance.value, // 将搜索结果标记到地图上
        panel: 'resultPanel', // 不显示结果面板
      });

      infoWindow.value = new window.AMap.InfoWindow({ offset: new window.AMap.Pixel(0, -30) });
    });

    // 监听地图移动结束事件，更新附近POI
    mapInstance.value.on('moveend', () => {
      updateMapState();
      loadNearbyPois();
    });
    // 监听地图缩放结束事件
    mapInstance.value.on('zoomend', () => {
      updateMapState();
      loadNearbyPois();
    });

    // 初始化后立即获取一次地图状态和加载POI
    updateMapState();
    setTimeout(() => {
      loadNearbyPois();
    }, 500); // 延迟加载，确保地图完全初始化

  } else {
    console.error('高德地图JS API未加载或地图容器不存在');
    // 如果地图加载失败，可以尝试重试或显示错误信息
    setTimeout(initMap, 1000); // 1秒后重试
  }
}

// 更新地图中心点和边界
const updateMapState = () => {
  if (mapInstance.value) {
    const center = mapInstance.value.getCenter();
    currentMapCenter.value = { lat: center.lat, lng: center.lng };
    currentMapBounds.value = mapInstance.value.getBounds(); // 获取当前可视区域
  }
}

// 在地图上添加 POI 标记
const addPoiMarkers = (pois) => {
  if (!mapInstance.value) return;

  // 清除旧的标记
  mapInstance.value.remove(currentMarkers.value);
  currentMarkers.value = [];

  const newMarkers = [];
  pois.forEach(poi => {
    // 确保有经纬度信息
    const lng = poi.longitude || (poi.location && poi.location.lng);
    const lat = poi.latitude || (poi.location && poi.location.lat);

    if (lng && lat) {
      // 根据类型设置不同的图标颜色
      let iconOptions = {};
      if (poi.type === 'hotel') {
        // 酒店使用蓝色标记
        iconOptions = {
          icon: new window.AMap.Icon({
            size: new window.AMap.Size(25, 34), // 图标尺寸
            image: '//webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
            imageSize: new window.AMap.Size(25, 34)
          })
        };
      } else {
        // 普通POI使用红色标记
        iconOptions = {
          icon: new window.AMap.Icon({
            size: new window.AMap.Size(25, 34), // 图标尺寸
            image: '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png',
            imageSize: new window.AMap.Size(25, 34)
          })
        };
      }

      const marker = new window.AMap.Marker({
        position: new window.AMap.LngLat(lng, lat),
        title: poi.poi_name || poi.name,
        ...iconOptions
      });

      // 为标记添加点击事件
      marker.on('click', (e) => {
        selectPoi(poi); // 选中列表中的POI
        // 显示信息窗体
        infoWindow.value.setContent(`
          <div>
            <h4>${poi.poi_name || poi.name}</h4>
            <p>地址: ${poi.address || '未知'}</p>
            <p>
            类型: ${poi.poi_type || poi.type || '未知'}
          </p>

          </div>
        `);
        infoWindow.value.open(mapInstance.value, marker.getPosition());
      });

      newMarkers.push(marker);
    }
  });

  mapInstance.value.add(newMarkers);
  currentMarkers.value = newMarkers;
}

// --- POI 搜索功能 (高德 PlaceSearch) ---
const handleSearch = () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词');
    return;
  }
  if (!placeSearch.value) {
    ElMessage.error('地图搜索服务未加载');
    return;
  }

  placeSearch.value.search(searchKeyword.value, (status, result) => {
    if (status === 'complete' && result.pois && result.pois.length > 0) {
      nearbyPois.value = result.pois.map(p => ({
        poi_id: p.id,
        poi_name: p.name,
        poi_type: p.type.split(';')[0], // 取第一个类型
        address: p.address,
        latitude: p.location.lat,
        longitude: p.location.lng,
        location: p.location // 兼容高德原生的location
      }));
      ElMessage.success(`找到 ${nearbyPois.value.length} 个相关地点`);
      // 移动地图到第一个搜索结果
      if (result.pois[0].location) {
        mapInstance.value.setCenter([result.pois[0].location.lng, result.pois[0].location.lat]);
      }
      showSuggestions.value = false; // 隐藏建议
      addPoiMarkers(nearbyPois.value); // 在地图上添加标记
    } else {
      nearbyPois.value = [];
      ElMessage.warning('未找到相关地点');
    }
  });
}

// --- 加载附近 POI 和酒店 (从你的后端 API) ---
const loadNearbyPois = async () => {
  poisLoading.value = true;
  try {
    // 获取所有POI数据，使用分页获取全部数据
    let allPois = [];
    let page = 1;
    const pageSize = 100;

    // 首先获取POI总数
    const poiCountResponse = await axios.get('http://127.0.0.1:8000/api/attractions/pois/', {
      params: { page: 1, page_size: 1 }
    });
    const poiTotalCount = poiCountResponse.data.count || 0;

    if (poiTotalCount > 0) {
      // 计算总页数并获取所有POI数据
      const totalPages = Math.ceil(poiTotalCount / pageSize);

      for (let i = 1; i <= totalPages; i++) {
        const response = await axios.get('http://127.0.0.1:8000/api/attractions/pois/', {
          params: { page: i, page_size: pageSize }
        });

        const data = response.data;
        const pois = data.results || data;
        allPois = allPois.concat(pois);
      }
    }

    // 获取所有酒店数据，使用分页获取全部数据
    let allHotels = [];
    // 首先获取酒店总数
    try {
      const hotelCountResponse = await axios.get('http://127.0.0.1:8000/api/hotels/hotels/', {
        params: { page: 1, page_size: 1 }
      });
      const hotelTotalCount = hotelCountResponse.data.count || 0;

      if (hotelTotalCount > 0) {
        // 计算总页数并获取所有酒店数据
        const hotelTotalPages = Math.ceil(hotelTotalCount / pageSize);

        for (let i = 1; i <= hotelTotalPages; i++) {
          const response = await axios.get('http://127.0.0.1:8000/api/hotels/hotels/', {
            params: { page: i, page_size: pageSize }
          });

          const data = response.data;
          const hotels = data.results || data;
          allHotels = allHotels.concat(hotels);
        }
      }
    } catch (hotelError) {
      console.error('获取酒店数据失败:', hotelError);
      // 如果酒店API失败，继续加载POI数据
    }

    // 合并POI和酒店数据，并标记类型
    const allData = [
      ...allPois.map(poi => ({ ...poi, type: 'poi', poi_type: '景点' })),
      ...allHotels.map(hotel => ({ ...hotel, type: 'hotel', poi_type: '酒店', poi_name: hotel.hotel_name || hotel.name }))
    ];

    // 过滤掉没有坐标的POI/酒店，或者为没有坐标的POI/酒店生成模拟坐标
    nearbyPois.value = allData.map(item => {
      if (!item.latitude || !item.longitude) {
        // 为没有坐标的POI/酒店生成模拟坐标 near the map center
        item.latitude = currentMapCenter.value.lat + (Math.random() - 0.5) * 0.01;
        item.longitude = currentMapCenter.value.lng + (Math.random() - 0.5) * 0.01;
      }
      return item;
    });

    addPoiMarkers(nearbyPois.value); // 将从后端获取的POI和酒店添加到地图上
    console.log('加载了', nearbyPois.value.length, '个POI和酒店'); // 调试信息

  } catch (error) {
    console.error('加载附近POI和酒店失败:', error);
    ElMessage.error('加载附近POI和酒店失败');
    nearbyPois.value = [];
    addPoiMarkers([]); // 清除地图上的标记
  } finally {
    poisLoading.value = false;
  }
}

// 选择POI，高亮显示并移动地图
const selectPoi = async (poi) => {
  selectedPoi.value = poi;

  // 尝试获取该POI的占用率信息
  let occupancyRate = null;
  try {
    // 根据POI ID查询动态数据获取占用率
    const dynamicResponse = await axios.get('http://127.0.0.1:8000/api/attractions/dynamic/', {
      params: {
        poi: poi.poi_id || poi.id,
        page: 1,
        page_size: 1
      }
    });
    const dynamicData = dynamicResponse.data.results || dynamicResponse.data;
    if (dynamicData.length > 0) {
      // 获取最新的一条动态数据的占用率
      const latestDynamic = dynamicData[0];
      occupancyRate = latestDynamic.occupancy_rate;
    }
  } catch (error) {
    console.error('获取占用率数据失败:', error);
    // 如果获取占用率失败，继续添加POI到列表
  }

// 尝试获取该POI是否受天气预警影响
let weatherAlertStatus = '无预警';
const affectedPoiIds = new Set(); // 使用Set来存储受影响的POI ID，方便快速查找

try {
  // 查询受预警影响的POI列表
  const response = await axios.get('http://127.0.0.1:8000/api/reviews/alert-affected-pois/', {
    params: {
      // 这里的poi_id参数可能不需要，如果你想获取所有受影响的POI，
      // 如果你只想获取特定POI是否受影响，那么这个参数还是有用的。
      // 根据你的描述“遍历api的poi字段建表”，我假设你希望获取所有受影响的POI。
      // 如果你确实只需要判断当前poi是否受影响，并且API能够直接返回一个单一结果，
      // 那么这里的逻辑会更简单，但根据你提供的API返回值，它是一个列表，所以下面的处理方式更通用。
      // 如果API只返回当前POI是否受影响，那么这一行可以保留，但下方的遍历就不需要了。
      poi_id: poi.poi_id || poi.id // 保留此行，以防API支持按ID过滤
    }
  });

  const affectedData = response.data.results || response.data;

  // 遍历API返回的受影响POI列表，将它们的ID添加到Set中
  if (Array.isArray(affectedData)) { // 确保是数组
    affectedData.forEach(item => {
      if (item.poi) { // 确保item.poi存在
        affectedPoiIds.add(item.poi);
      }
    });
  }

  // 检查当前POI的ID是否在受影响的ID集合中
  const currentPoiId = poi.poi_id || poi.id;
  if (currentPoiId && affectedPoiIds.has(currentPoiId)) {
    weatherAlertStatus = '受影响';
  }

} catch (error) {
  console.error('获取天气预警状态失败:', error);
  // 如果获取天气预警状态失败，继续添加POI到列表
}

// 添加到已点击景点记录（避免重复）
const exists = clickedScenicList.value.some(item =>
  item.poi_id === poi.poi_id ||
  item.h_id === poi.h_id ||
  item.id === poi.id
);


  if (!exists) {
    clickedScenicList.value.push({
      poi_name: poi.poi_name || poi.hotel_name || poi.name,
      poi_type: poi.type === 'hotel' ? '酒店' : (poi.poi_type || poi.type || 'POI'),
      address: poi.address || '地址未知',
      occupancy_rate: occupancyRate,
      weather_alert_status: weatherAlertStatus,
      poi_id: poi.poi_id,
      h_id: poi.h_id,
      id: poi.id
    });
  }

  // 移动地图到选中的POI
  const lng = poi.longitude || (poi.location && poi.location.lng);
  const lat = poi.latitude || (poi.location && poi.location.lat);
  if (lng && lat && mapInstance.value) {
    mapInstance.value.setCenter([lng, lat]);
    // 可以在这里打开信息窗体
    infoWindow.value.setContent(`
      <div>
        <h4>${poi.poi_name || poi.hotel_name || poi.name}</h4>
        <p>地址: ${poi.address || '未知'}</p>
        <p>类型: ${poi.type === 'hotel' ? '酒店' : (poi.poi_type || poi.type || '未知')}</p>
      </div>
    `);
    infoWindow.value.open(mapInstance.value, new window.AMap.LngLat(lng, lat));
  }
}

// 清空已点击景点记录
const clearClickedList = () => {
  clickedScenicList.value = [];
}

// --- 生命周期钩子 ---
onMounted(() => {
  initMap(); // 初始化地图
});

onUnmounted(() => {
  if (mapInstance.value) {
    mapInstance.value.destroy(); // 销毁地图实例，释放资源
    mapInstance.value = null;
  }
  // 清理 PlaceSearch 实例 (如果需要)
  if (placeSearch.value) {
      placeSearch.value = null;
  }
  if (infoWindow.value) {
      infoWindow.value = null;
  }
});
</script>

<style scoped>
/* 保持大部分样式不变，但调整地图相关样式 */
.map-poi-view {
  width: 100%;
  height: 100vh;
  display: flex;
}

.map-container {
  display: flex;
  flex: 1;
  position: relative;
}

.map {
  flex: 1;
  /* 背景渐变和动画不再需要，由高德地图SDK渲染 */
  /* background: linear-gradient(45deg, #e3f2fd, #bbdefb, #90caf9); */
  /* background-size: 400% 400%; */
  /* animation: gradient 10s ease infinite; */
  position: relative;
  overflow: hidden;
  /* cursor: grab; 由SDK控制鼠标样式 */
}

/* 移除模拟拖拽的 active 样式 */
/* .map:active {
  cursor: grabbing;
} */

.map-overlay {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 10;
  width: 350px; /* 调整宽度以适应搜索建议 */
  background: rgba(255, 255, 255, 0.9); /* 为 overlay 添加背景，避免被地图覆盖 */
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.search-box {
  display: flex;
  gap: 10px;
}

.search-suggestions {
  position: absolute;
  top: 50px; /* 位于搜索框下方 */
  left: 10px;
  right: 10px;
  background: white;
  border: 1px solid #e4e7ed;
  border-top: none;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-height: 200px;
  overflow-y: auto;
  z-index: 11;
}

.suggestion-item {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover {
  background-color: #f5f7fa;
}

/* POI标记由SDK渲染，不再需要自定义poi-marker样式 */
/* .poi-marker { ... } */
/* .poi-icon { ... } */
/* .poi-label { ... } */


.info-panel {
  width: 350px;
  background: white;
  border-left: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 10; /* 确保信息面板在地图上方 */
}

.panel-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.poi-list {
  flex: 1;
  overflow-y: auto;
}

.poi-item {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s;
}

.poi-item:hover {
  background-color: #f5f7fa;
}

.poi-item.active {
  background-color: #ecf5ff;
  border-left: 3px solid #409eff;
}

.poi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.poi-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.poi-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.poi-info div {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #606266;
}

.poi-coords {
  color: #909399;
}

/* 滚动条样式 */
:deep(.el-scrollbar__wrap) {
  overflow-x: hidden;
}
</style>