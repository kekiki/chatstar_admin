import requests
from fastapi import HTTPException
import logging

from config import ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN, ZOHO_ACCOUNT_URL, ZOHO_ORG_ID, ZOHO_ROOT_FOLDER_ID

logger = logging.getLogger("zoho_workdrive")
logger.propagate = False
logger.setLevel(logging.DEBUG)

# 文件处理器，日志写入 workdrive.log
file_handler = logging.FileHandler("zoho_workdrive.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(log_format)

logger.addHandler(file_handler)
logger.info("测试")

class ZohoWorkDrive:
    def __init__(self):
        self.client_id = ZOHO_CLIENT_ID
        self.client_secret = ZOHO_CLIENT_SECRET
        self.refresh_token = ZOHO_REFRESH_TOKEN
        self.account_url = ZOHO_ACCOUNT_URL
        self.folder_id = ZOHO_ROOT_FOLDER_ID
        self.org_id = ZOHO_ORG_ID
        self.api_base = "https://workdrive.zoho.com/api/v1"
        self.access_token = None
        self._refresh_access_token()

    def _refresh_access_token(self):
        """用refresh_token自动刷新access_token，过期自动调用"""
        logger.info("开始刷新Zoho WorkDrive access_token")
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }
        resp = requests.post(f"{self.account_url}/oauth/v2/token", data=payload)
        data = resp.json()
        if "access_token" not in data:
            logger.error(f"令牌刷新失败: {data}")
            raise Exception("Token refresh failed")
        self.access_token = data["access_token"]
        logger.info("access_token刷新成功")

    def _request(self, endpoint, method="GET", params=None, json=None, files=None):
        """通用请求封装，401自动重试刷新令牌"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.api_base}{endpoint}"
        try:
            if method == "GET":
                res = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                if files:
                    res = requests.post(url, headers=headers, params=params, files=files)
                else:
                    res = requests.post(url, headers=headers, json=json)
            elif method == "DELETE":
                res = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError("不支持的请求方法")

            # token过期，刷新后重试一次
            if res.status_code == 401:
                logger.warning("access_token失效，重新刷新并重试请求")
                self._refresh_access_token()
                headers["Authorization"] = f"Bearer {self.access_token}"
                res = requests.get(url, headers=headers, params=params) if method=="GET" else requests.post(url, headers=headers, json=json, files=files)

            res_data = res.json()
            logger.debug(f"API请求 {method} {endpoint} 返回: {res_data}")
            return res_data
        except Exception as e:
            logger.error(f"API调用异常: {str(e)}", exc_info=True)
            raise

    # ===================== 原有工具方法 =====================
    def get_teams(self):
        """获取团队列表，拿到team_id"""
        return self._request("/teams")

    def list_folder_files(self, parent_folder_id: str):
        """列出文件夹内所有文件"""
        return self._request("/files", params={"parent_id": parent_folder_id})

    # ===================== 新增1：bytes字节流上传 =====================
    def upload_bytes(self, parent_folder_id: str, file_bytes: bytes, file_name: str):
        """
        直接上传二进制字节，无需本地文件
        :param parent_folder_id: 目标文件夹ID
        :param file_bytes: 文件二进制bytes
        :param file_name: 上传后的文件名（带后缀，如test.jpg）
        :return: 上传结果dict，包含file_id
        """
        logger.info(f"开始字节流上传文件: {file_name}，目标文件夹 {parent_folder_id}")
        params = {
            "parent_id": parent_folder_id,
            "filename": file_name
        }
        # bytes封装成文件对象传给files
        upload_files = {
            "content": (file_name, file_bytes)
        }
        upload_resp = self._request("/upload", method="POST", params=params, files=upload_files)
        file_data = upload_resp.get("data", [])[0]
        file_id = file_data.get('attributes', {}).get('resource_id')
        logger.info(f"文件{file_name}上传完成，file_id={file_id}")
        return {
            "file_id": file_id
        }

    # ===================== 新增2：生成公开直链 =====================
    def create_public_link(self, file_id: str, download_only: bool = True):
        """
        给文件创建公开分享直链（任何人可访问下载）
        :param file_id: 上传返回的文件ID
        :param download_only: True=仅下载，False=在线预览页面
        :return: 公开链接信息，含download_url直链
        """
        logger.info(f"为文件{file_id}创建公开分享链接")
        payload = {
            "access": "public",
            "download_only": download_only,
            # "password_protect": False,
            "expiry_days": 0  # 0=永久有效
        }
        resp = self._request(f"/files/{file_id}/share", method="POST", json=payload)
        share_data = resp.get("data", {})
        # 提取直接下载地址
        direct_download_url = share_data.get("download_url")
        logger.info(f"公开直链生成成功: {direct_download_url}")
        return {
            "share_info": share_data,
            "direct_url": direct_download_url
        }

    def upload_and_get_link(self, file_bytes: bytes, file_name: str) -> dict:
        """
        一站式：上传二进制文件 + 自动生成公开下载直链
        """
        upload_res = self.upload_bytes(self.folder_id, file_bytes, file_name)
        file_id = upload_res["file_id"]
        link_res = self.create_public_link(file_id)
        return {
            "file_info": upload_res,
            "direct_url": link_res["direct_url"]
        }