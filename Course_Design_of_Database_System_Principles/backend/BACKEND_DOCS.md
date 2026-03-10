# 文旅资源管理系统 - 后端文档

## 项目概述

文旅资源管理系统是一个基于 Django 和 Django REST Framework 构建的智慧旅游平台后端系统。该系统专注于文旅资源的全景管理、旅游企业与运营关联、动态运行监测分析、精准气象服务以及应急预警与风险管控。

### 项目架构
- **框架**: Django 4.2 + Django REST Framework
- **数据库**: SQLite (开发环境) / MySQL (生产环境)
- **缓存**: Redis (可选)
- **消息队列**: Celery (可选)
- **API 文档**: Swagger / ReDoc
- **认证方式**: Token 认证

## 项目结构

```
backend/
├── apps/                   # 应用模块
│   ├── attractions/        # 文旅资源管理
│   ├── common/             # 公共组件
│   ├── hotels/             # 酒店管理
│   ├── orders/             # 订单管理
│   ├── reviews/            # 评价与天气
│   └── users/              # 用户管理
├── config/                 # 配置文件
│   ├── settings/           # 环境配置
│   │   ├── base.py        # 基础配置
│   │   ├── dev.py         # 开发配置
│   │   └── prod.py        # 生产配置
│   ├── urls.py            # 主路由
│   └── wsgi.py
├── db.sqlite3             # SQLite 数据库文件
├── requirements.txt       # 依赖包列表
├── manage.py              # Django 管理脚本
├── .env                   # 环境变量配置
└── docker-compose.yml     # Docker 配置
```

## 技术栈

### 核心依赖
- `django`: Web 框架
- `djangorestframework`: REST API 框架
- `django-cors-headers`: CORS 支持
- `drf-yasg`: API 文档生成
- `django-filter`: 查询过滤
- `celery`: 异步任务处理
- `mysqlclient`: MySQL 数据库驱动
- `django-extensions`: Django 扩展工具

## 环境配置

### 环境变量配置

创建 `.env` 文件并配置以下变量：

```bash
# Django 配置
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
DB_ENGINE=django.db.backends.sqlite3  # 或 django.db.backends.mysql
DB_NAME=tourism_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Redis 配置（可选）
REDIS_ENABLED=False
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery 配置（可选）
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 本地开发环境搭建

1. **克隆项目并进入目录**
   ```bash
   cd backend
   ```

2. **创建虚拟环境并安装依赖**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **配置数据库**
   ```bash
   # 创建数据库迁移
   python manage.py makemigrations
   
   # 执行数据库迁移
   python manage.py migrate
   
   # 创建超级用户（可选）
   python manage.py createsuperuser
   ```

4. **启动开发服务器**
   ```bash
   python manage.py runserver
   ```

## 数据库模型

### 用户模型 (User)
- **表名**: `users`
- **字段**:
  - `id`: 主键
  - `username`: 用户名
  - `email`: 邮箱
  - `phone`: 手机号
  - `avatar`: 头像
  - `created_at`: 创建时间
  - `updated_at`: 更新时间

### 文旅资源模型 (Poimaster)
- **表名**: `poimaster`
- **字段**:
  - `poi_id`: 资源点ID (主键)
  - `poi_name`: 资源点名称
  - `poi_type`: 资源点类型 (景区、酒店、餐厅等)
  - `address`: 地址
  - `longitude`: 经度
  - `latitude`: 纬度
  - `description`: 描述

### 景区详情模型 (Scenicspotdetails)
- **表名**: `scenicspotdetails`
- **字段**:
  - `s_id`: 景区详情ID (主键)
  - `scenic_spot`: 关联POI
  - `level`: 景区级别 (5A、4A等)
  - `max_capacity`: 最大承载量

### 动态数据模型 (Dynamicdata)
- **表名**: `dynamicdata`
- **字段**:
  - `record_id`: 记录ID (主键)
  - `poi`: 关联POI
  - `record_time`: 记录时间
  - `passenger_flow`: 客流量
  - `occupancy_rate`: 入住率/占用率

### 酒店详情模型 (Hoteldetails)
- **表名**: `hoteldetails`
- **字段**:
  - `h_id`: 酒店详情ID (主键)
  - `hotel`: 关联POI
  - `scenic_spot_detail`: 所属景区
  - `star_rating`: 星级
  - `room_count`: 房间数量

### 位置天气模型 (Locationweather)
- **表名**: `locationweather`
- **字段**:
  - `location_id`: 位置ID (主键)
  - `location_name`: 位置名称
  - `longitude`: 经度
  - `latitude`: 纬度
  - `poi`: 关联POI
  - `temperature`: 温度
  - `conditions`: 天气状况
  - `update_time`: 更新时间

### 天气预警模型 (Weatheralert)
- **表名**: `weatheralert`
- **字段**:
  - `alert_id`: 预警ID (主键)
  - `title`: 预警标题
  - `level`: 预警级别 (红色、橙色、黄色、蓝色)
  - `status`: 预警状态
  - `publish_time`: 发布时间

### 企业信息模型 (Enterpriseinfo)
- **表名**: `enterpriseinfo`
- **字段**:
  - `enterprise_id`: 企业ID (主键)
  - `enterprise_name`: 企业名称
  - `enterprise_type`: 企业类型

### 企业POI关联模型 (Enterprisepoilink)
- **表名**: `enterprisepoilink`
- **字段**:
  - `e_id`: 关联ID (主键)
  - `enterprise`: 企业
  - `poi`: POI资源点
  - `relationship_type`: 关系类型

## API 接口文档

### 用户模块 (Users)

#### 用户注册
- **URL**: `POST /api/v1/users/register/`
- **请求体**:
  ```json
  {
    "username": "用户名",
    "password": "密码",
    "email": "邮箱"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "注册成功",
    "data": {
      "username": "用户名",
      "email": "邮箱"
    }
  }
  ```

#### 用户登录
- **URL**: `POST /api/v1/users/login/`
- **请求体**:
  ```json
  {
    "username": "用户名",
    "password": "密码"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "登录成功",
    "data": {
      "token": "认证令牌",
      "username": "用户名",
      "email": "邮箱",
      "is_staff": false
    }
  }
  ```

#### 获取用户信息
- **URL**: `GET /api/v1/users/profile/`
- **请求头**: `Authorization: Token <token>`
- **响应**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "username": "用户名",
      "email": "邮箱",
      "is_staff": false,
      "date_joined": "2023-01-01T00:00:00Z"
    }
  }
  ```

#### 用户登出
- **URL**: `POST /api/v1/users/logout/`
- **请求头**: `Authorization: Token <token>`
- **响应**:
  ```json
  {
    "code": 200,
    "message": "登出成功"
  }
  ```

### 文旅资源模块 (Attractions)

#### 获取POI列表
- **URL**: `GET /api/attractions/pois/`
- **参数**:
  - `poi_type`: POI类型过滤
  - `search`: 搜索关键词
  - `ordering`: 排序字段
- **响应**:
  ```json
  {
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
      {
        "poi_id": 1,
        "poi_name": "景点名称",
        "poi_type": "景区",
        "address": "地址",
        "longitude": "121.123456",
        "latitude": "31.123456",
        "description": "描述"
      }
    ]
  }
  ```

#### 搜索POI
- **URL**: `GET /api/attractions/pois/search/`
- **参数**:
  - `q`: 搜索关键词
  - `poi_type`: POI类型过滤
- **响应**: 同POI列表

#### 获取POI类型
- **URL**: `GET /api/attractions/pois/types/`
- **响应**:
  ```json
  [
    "景区",
    "酒店",
    "餐厅"
  ]
  ```

#### 获取附近POI
- **URL**: `GET /api/attractions/pois/{id}/nearby/`
- **参数**:
  - `radius`: 半径（公里），默认5
- **响应**: POI列表

#### 获取最新动态数据
- **URL**: `GET /api/attractions/dynamic/latest/`
- **参数**:
  - `poi_id`: POI ID
- **响应**:
  ```json
  {
    "record_id": 1,
    "poi": 1,
    "record_time": "2023-01-01T00:00:00Z",
    "passenger_flow": 100,
    "occupancy_rate": "85.50"
  }
  ```

### 酒店模块 (Hotels)

#### 获取酒店详情
- **URL**: `GET /api/hotels/hoteldetails/`
- **参数**:
  - `hotel`: 酒店POI ID过滤
  - `star_rating`: 星级过滤

### 天气与评价模块 (Reviews)

#### 获取位置天气
- **URL**: `GET /api/reviews/locationweather/`
- **参数**:
  - `poi`: POI ID过滤
  - `location_name`: 位置名称搜索

#### 获取天气预警
- **URL**: `GET /api/reviews/weatheralert/`
- **参数**:
  - `level`: 预警级别过滤
  - `status`: 预警状态过滤

### 订单模块 (Orders)

#### 获取企业信息
- **URL**: `GET /api/orders/enterpriseinfo/`
- **参数**:
  - `enterprise_type`: 企业类型过滤

#### 获取企业POI关联
- **URL**: `GET /api/orders/enterprisepoilink/`
- **参数**:
  - `enterprise`: 企业ID过滤
  - `poi`: POI ID过滤

## API 文档访问

- **Swagger UI**: `http://127.0.0.1:8000/swagger/`
- **ReDoc**: `http://127.0.0.1:8000/redoc/`
- **API 根路径**: `http://127.0.0.1:8000/api/v1/`

## 认证与授权

系统使用 Token 认证方式，用户登录后会获得认证令牌。在访问需要认证的 API 时，需要在请求头中添加：

```
Authorization: Token <your-token-here>
```

## 部署说明

### Docker 部署

1. **构建镜像**
   ```bash
   docker build -t tourism-backend .
   ```

2. **启动容器**
   ```bash
   docker-compose up -d
   ```

### 生产环境部署

1. **环境配置**
   - 设置 `DEBUG=False`
   - 配置生产数据库
   - 配置 Redis 缓存
   - 配置 Celery 任务队列

2. **静态文件收集**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **启动服务**
   - 使用 Gunicorn 或 uWSGI 启动 Django 应用
   - 启动 Celery worker 处理异步任务

## 开发规范

### 代码规范
- 遵循 PEP 8 代码风格
- 使用中文注释和文档
- 模型字段使用 verbose_name 标注

### API 设计规范
- 使用 RESTful API 设计
- 返回统一的响应格式
- 使用 HTTP 状态码表示操作结果
- 支持分页和过滤

### 数据库规范
- 使用 Django ORM
- 合理设计模型关系
- 添加适当的索引
- 使用迁移文件管理数据库变更

## 测试

### 运行测试
```bash
python manage.py test
```

### 测试覆盖
- 模型测试
- 视图测试
- API 测试
- 集成测试

## 维护与监控

### 日志配置
- 开发环境输出到控制台
- 生产环境输出到文件
- 记录关键操作和错误信息

### 性能监控
- 数据库查询优化
- 缓存策略
- 异步任务处理