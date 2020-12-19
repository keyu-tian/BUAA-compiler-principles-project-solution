# Copyright (C) 2020, Keyu Tian, Beihang University.
# This file is a part of my compiler assignment for Compilation Principles.
# All rights reserved.

from typing import Union

import bs4
import requests
from bs4 import BeautifulSoup


def parse_html(url, target_name=None) -> Union[BeautifulSoup, bs4.element.Tag]:
    html = requests.get(
        url=url,
        headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'},
        timeout=20
    )
    html.encoding = html.apparent_encoding
    bs = BeautifulSoup(html.text, 'html.parser')
    return bs if target_name is None else bs.find(target_name)

