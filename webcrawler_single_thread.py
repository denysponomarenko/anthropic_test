def crawl_same_host(start_url: str, provider: LinkProvider) -> Set[str]:
    host = get_hostname(start_url)

    visited = {start_url}
    queue = [start_url]

    while queue:
        url = queue.pop(0)

        for link in provider.get_links(url):
            if get_hostname(link) == host and link not in visited:
                visited.add(link)
                queue.append(link)

    return visited
