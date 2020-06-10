import base64
import json
import os

import github3


def _fetch_jons_json():
    g = github3.login(token=os.environ["SLOTH_GITHUB_TOKEN"])
    dotnet = g.repository('googleapis', 'google-cloud-dotnet')
    file_b64 = dotnet.file_contents('apis/ServiceDirectory/directory.json').content
    file_decoded = base64.b64decode(file_b64).decode('utf-8')
    return json.loads(file_decoded)


def _parse_jons_json(jons_json):
    services = []
    for service in jons_json.get("Services"):
        name = service.get("Name")
        if name not in services:
            services.append(name)
    return services


def get_published_services():
    file = _fetch_jons_json()
    return _parse_jons_json(file)


if __name__ == "__main__":
    service_versions = get_published_services()
    print(len(service_versions))
    print(service_versions)