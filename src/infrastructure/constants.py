"""
本模块包含 GOOSE 应用程序中使用的常量。
该模块集中管理所有魔法数字、字符串和配置值，
以提高可维护性并减少重复。
"""

# API Configuration
API_BASE_URL = "https://tyxsjpt.seu.edu.cn"
API_CHECK_TENANT_PATH = "/api/miniapp/anno/checkTenant"
API_CHECK_TOKEN_PATH = "/api/miniapp/student/checkToken"
API_SAVE_START_RECORD_PATH = "/api/exercise/exerciseRecord/saveStartRecord"
API_SAVE_RECORD_PATH = "/api/exercise/exerciseRecord/saveRecord"
API_UPLOAD_START_IMAGE_PATH = "/api/miniapp/exercise/uploadRecordImage"
API_UPLOAD_FINISH_IMAGE_PATH = "/api/miniapp/exercise/uploadRecordImage2"
API_LIST_ROUTE_PATH = "/api/miniapp/exercise/listRule"

# HTTP Headers
HEADER_TOKEN_PREFIX = "Bearer "
HEADER_XWEB_XHR = "1"
HEADER_CONTENT_TYPE_JSON = "application/json;charset=UTF-8"
HEADER_CONTENT_TYPE_JSON_SIMPLE = "application/json"
HEADER_ACCEPT = "*/*"
HEADER_SEC_FETCH_SITE = "cross-site"
HEADER_SEC_FETCH_MODE = "cors"
HEADER_SEC_FETCH_DEST = "empty"
HEADER_ACCEPT_ENCODING = "gzip, deflate, br"
HEADER_ACCEPT_LANGUAGE = "zh-CN,zh;q=0.9"

# Token Configuration
TOKEN_PARTS_COUNT = 3
TOKEN_USERID_FIELD = "userid"

# Exercise Calculations
CALORIE_PER_KM = 62  # 每公里消耗的卡路里
EARTH_RADIUS_KM = 6378.13649  # 地球半径（公里），用于Haversine公式

# API Response Codes
API_SUCCESS_CODE = 0
API_ERROR_INVALID_TENANT = -6
API_ERROR_INVALID_TOKEN = 40005

# Request Configuration
REQUEST_MIN_DELAY_SEC = 1.5  # 请求之间的最小延迟（秒）
REQUEST_MAX_DELAY_SEC = 3.5  # 请求之间的最大延迟（秒）

# Record Status
RECORD_STATUS_FINISHED = 2  # Status code for finished exercise record

# File Configuration
IMAGE_FILENAME = "1.jpg"  # Default filename for uploaded images
IMAGE_MIME_TYPE = "image/jpeg"  # MIME type for uploaded images
