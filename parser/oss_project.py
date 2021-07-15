from dataclasses import dataclass
from datetime import date
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import validators
from dateutil.parser import parse

from github_api import GithubRepo
from project_types import Activity, License

# TODO: ist this a good approach?
# class Category(Enum):
#     MODELING
#     SIMULATION
#     INTERFACES
#     PLATFORM
#     FORECASTING
#     STATE_ESTIMATION
#     OPTIMIZATION
#     POWER_QUALITY
#     FIRMWARE
#     ALGORITHMS


@dataclass
class OpenSourceProject:
    """Class for keeping track of an item in inventory."""

    # mandatory
    name: str
    repository: str
    description: str

    # optional
    homepage: Optional[str]

    # auto generated if not given
    license_name: Optional[License]
    languages: Optional[List[str]]
    tags: Optional[List[str]]
    first_release: Optional[Activity]

    # auto generated
    # category: str
    last_update: Optional[Activity]
    latest_release: Optional[Activity]

    # Ideas:
    # Contributors
    # CI/Coverage

    @classmethod
    def from_dict(cls, d: dict) -> "OpenSourceProject":
        def get_dict_value(
            d: Dict[str, Any], key: str, validator: Callable[[str], bool] = None
        ) -> Optional[Any]:
            if not key in d:
                return None
            val = d[key]
            if not val:
                return None
            if validator is not None:
                # TODO: maybe raise exception if value is invalid?
                if not validator(val):
                    return None
            return val

        # Mandatory
        name = get_dict_value(d, "name")
        assert isinstance(name, str), "Project needs to have a name!"

        repository = get_dict_value(d, "repository")
        assert isinstance(repository, str), "Project needs to have a valid url!"

        repo_api = None
        parsed_repo_url = urlparse(repository)
        if parsed_repo_url.netloc == "github.com":
            repo_api = GithubRepo(repository)

        description = get_dict_value(d, "description")
        assert isinstance(
            description, str
        ), "Project needs to have a proper description!"

        # Manual
        homepage = get_dict_value(d, "homepage", validators.url)

        # Semi autogenerated

        license_usr = get_dict_value(d, "license")
        if license_usr is None and repo_api is not None:
            license_name = repo_api.get_license()
        else:
            assert isinstance(license_usr, str)
            license_name = License(license_usr, None)

        first_release_str = get_dict_value(d, "first_release")
        first_release = None
        if first_release_str is not None:
            first_release = Activity(parse(first_release_str).date(), None)
        elif repo_api is not None:
            first_release = repo_api.get_first_release()

        languages = get_dict_value(d, "languages")
        # TODO: Convert to list
        # TODO: get languages from API

        tags = get_dict_value(d, "tags")
        # TODO: Convert to list
        # TODO: get languages from API

        # Autogenerated

        # TODO: generate from API
        last_update = None
        if repo_api is not None:
            last_update = repo_api.get_last_activity()

        latest_release = None
        if repo_api is not None:
            latest_release = repo_api.get_latest_release()

        return cls(
            name=name,
            repository=repository,
            description=description,
            homepage=homepage,
            license_name=license_name,
            languages=languages,
            tags=tags,
            # category=category,
            last_update=last_update,
            latest_release=latest_release,
            first_release=first_release,
        )

    @classmethod
    def list_headers(cls):
        return [
            "Project",
            "Repository URL",
            "Description",
            "Homepage",
            "License",
            "Languages",
            "Tags",
            # "Category",
            "Last Update",
            "Latest Release",
            "First Release",
        ]

    def to_list(self) -> List[str]:
        def simple_url(url: str) -> str:
            retval = f'<a href="{url}">{url}</a>'
            return retval

        def fmt_release(release):
            if release is not None:
                retval = f"{release[0]} - ({simple_url(release[1])})"
                return retval
            else:
                return ""

        def safe_fmt(o: Optional[Any], formatter: Callable[[Any], str]):
            if o:
                return formatter(o)
            else:
                return ""

        return [
            self.name,
            safe_fmt(self.repository, simple_url),
            self.description,
            safe_fmt(self.homepage, simple_url),
            safe_fmt(self.license_name, License.as_html),
            safe_fmt(self.languages, str),
            safe_fmt(self.tags, str),
            # self.category,
            safe_fmt(self.last_update, Activity.as_html),
            safe_fmt(self.latest_release, Activity.as_html),
            safe_fmt(self.first_release, Activity.as_html),
        ]
