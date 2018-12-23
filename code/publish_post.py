#! usr/bin/env python3

import os
from helpers import fetchPosts, hasBeenPublished, pushPostToMedium


def publishPostsMedium():
    fetched_posts_titles = fetchPosts()
    posts_to_publish = hasBeenPublished(fetched_posts=fetched_posts_titles)

    for key, value in posts_to_publish.items():
        if value:
            request_resp = pushPostToMedium(post=key)
            print(request_resp)

    return posts_to_publish

publishPostsMedium()