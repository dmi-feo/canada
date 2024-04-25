import abc
from typing import Optional

import attr

from canada.yt_wb_manager import constants as yt_const


@attr.s(slots=True)
class YTAuthData:
    cookies: dict[str, str] = attr.ib()
    headers: dict[str, str] = attr.ib()


class BaseYTAuthContext(abc.ABC):
    @abc.abstractmethod
    def get_auth_data(self, cookies: dict[str, str], headers: dict[str, str]) -> YTAuthData:
        pass


class YTNoAuthContext(BaseYTAuthContext):
    def get_auth_data(self, cookies: dict[str, str], headers: dict[str, str]) -> YTAuthData:
        return YTAuthData(cookies=cookies, headers=headers)


@attr.s(slots=True)
class YTCookieAuthContext(BaseYTAuthContext):
    cypress_cookie: str = attr.ib(repr=False)
    csrf_token: Optional[str] = attr.ib(repr=False)

    def get_auth_data(self, cookies: dict[str, str], headers: dict[str, str]) -> YTAuthData:
        cookies = cookies.copy()
        cookies[yt_const.YT_COOKIE_TOKEN_NAME] = self.cypress_cookie
        if self.csrf_token:
            headers = headers.copy()
            headers[yt_const.YT_HEADER_CSRF_NAME] = self.csrf_token
        return YTAuthData(cookies=cookies, headers=headers)
