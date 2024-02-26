import abc

import attr

from canada.yt_wb_manager import constants as yt_const


class BaseYTAuthContext(abc.ABC):
    @abc.abstractmethod
    def mutate_auth_data(self, cookies: dict[str, str], headers: dict[str, str]):
        pass


class YTNoAuthContext(BaseYTAuthContext):
    def mutate_auth_data(self, cookies: dict[str, str], headers: dict[str, str]):
        pass


@attr.s(slots=True)
class YTCookieAuthContext(BaseYTAuthContext):
    cypress_cookie: str = attr.ib(repr=False)
    csrf_token: str = attr.ib(repr=False)

    def mutate_auth_data(self, cookies: dict[str, str], headers: dict[str, str]):
        cookies[yt_const.YT_COOKIE_TOKEN_NAME] = self.cypress_cookie
        headers[yt_const.YT_HEADER_CSRF_NAME] = self.csrf_token
