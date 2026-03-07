from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http.response import HttpResponseForbidden

from .utils import get_client_ip


class IPRateLimitMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = get_client_ip(request)
        key = f"ip_rate_limit_{ip}"
        count = cache.get(key, 0)

        if count >= 30:
            return HttpResponseForbidden("访问过于频繁，请稍后再试")

        cache.set(key, count + 1, 200)  # 一分钟内最多访问1000次
