import base64
import json

import github3

from utils import _get_secret


def _fetch_jons_json():
    token = _get_secret("client-coverage-status-ghtoken", "latest")
    g = github3.login(token=token)
    dotnet = g.repository("googleapis", "google-cloud-dotnet")
    file_b64 = dotnet.file_contents("apis/ServiceDirectory/directory.json").content
    file_decoded = base64.b64decode(file_b64).decode("utf-8")
    return json.loads(file_decoded)


def _parse_jons_json(jons_json):
    services = {}
    for service in jons_json.get("Services"):
        name = service.get("Name")
        version = service.get("Version")
        if name in services.keys():
            if version not in services.get(name).get("versions"):
                services[name]["versions"].append(version)
        else:
            services[name] = {"title": service.get("Title"), "versions": [version]}
    return services


def get_published_protos():
    apis_json = _fetch_jons_json()
    protos = _parse_jons_json(apis_json)
    print(f"googleapis: found {len(protos)} services.")
    return protos


if __name__ == "__main__":
    import pprint

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(get_published_protos())
