class DfxApi:
    rest_url = "https://api2.api.deepaffex.ai:9443"
    device_id = ""
    device_token = ""
    role_id = ""
    user_id = ""
    user_token = ""


from .Organizations import Organizations
from .Users import Users
from .Measurements import Measurements
