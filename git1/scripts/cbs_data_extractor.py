# 示例：在scripts/extract.py中添加功能
import requests

def fetch_cbs_data():
    """Fetch data from Dutch Central Bureau of Statistics API"""
    response = requests.get("https://opendata.cbs.nl/ODataApi/odata/83710NED/TypedDataSet")
    return response.json()