import collections

import requests


class Summary:
    def __init__(self, smmry_dict, params, response):
        self.params = params
        self.api_url = response.url
        self.sm_url = params["SM_URL"]
        self.smmry_dict = smmry_dict
        self.sm_length = 7

        for key, value in smmry_dict.items():
            setattr(self, key, value)


class SmmryException(Exception):
    pass


class SmmryAPI:
    def __init__(self, key):

        self.key = key
        self.endpoint = "http://api.smmry.com/"

    def params(self, url, args_dict):
        params = collections.OrderedDict(args_dict)

        params.update({"sm_api_key": self.key})
        params.update({"sm_url": url})

        return {k.upper(): v for k, v in params.items()}

    def summarize(self, url, **args):

        params = self.params(url, args)

        response = requests.post(self.endpoint, params=params)
        response.close()

        smmry_dict = response.json()

        if smmry_dict.get("sm_api_error"):
            raise SmmryException(
                f"{smmry_dict['sm_api_error']}: {smmry_dict['sm_api_message']}"
            )

        if params.get("SM_WITH_BREAK"):
            smmry_dict["sm_api_content"] = smmry_dict["sm_api_content"].replace(
                "[BREAK]", params["SM_WITH_BREAK"]
            )

        smmry_dict["sm_api_content"] = smmry_dict["sm_api_content"].strip()

        return Summary(smmry_dict, params, response)
