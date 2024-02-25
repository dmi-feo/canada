import abc

import attr

from canada import constants


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
        cookies[constants.YT_COOKIE_TOKEN_NAME] = self.cypress_cookie
        headers[constants.YT_HEADER_CSRF_NAME] = self.csrf_token
