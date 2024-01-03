
from enum import Enum
from pydantic import BaseModel

class UserAgentEnum(str, Enum):
    chrome = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537"
    firefox = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0"
    edge = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134"
    curl = "curl/7.74.0"
    python_requests = "python-requests/2.25.1"
    ie = "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko"
    safari_iphone = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
    googlebot = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    bingbot = "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"


class Message(BaseModel):
    status: str


