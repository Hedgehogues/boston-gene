import json
import re

import requests
from copy import deepcopy


class FilesClient:
    """
    FilesClient connects to gdc-api and gets all files by filters (like gdc-api, see config)

    :param batch_size: batch size of request
    :param filters: filters (like dgc-api)
    :param fields: fields for request
    :param endpoint: endpoint
    """
    def __init__(self, batch_size, filters, fields, endpoint):
        self.batch_size = batch_size
        self.filters = filters
        self.fields = fields
        self.endpoint = endpoint

    def __make_request(self, project_id, size, from_):
        extension_filters = deepcopy(self.filters)
        extension_filters["content"].append({
            "op": "=",
            "content": {
                "field": "cases.project.project_id",
                "value": project_id,
            },
        })
        extension_filters = json.dumps(extension_filters)
        params = {
            "filters": extension_filters,
            "fields": self.fields,
            "size": size,
            "from": from_,
        }
        response = requests.get(self.endpoint, params=params)
        # TODO: warning proceproject_idssing
        return response.json()['data']

    def get_files(self, project_id):
        """

        :param project_id: gdc project id
        :return: list of files (like gdc-api fileds hits)
        """
        responses = []
        hits = None
        step = 0
        while hits is None or len(hits) == self.batch_size:
            response = self.__make_request(project_id, self.batch_size, step)
            hits = response['hits']
            responses += hits
            step += self.batch_size
        return responses


class DataClient:
    """
    DataClient go to gdc-api and request archives with data by file ids

    :param endpoint: endpoint
    """
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def get_files(self, ids):
        """
        This this handler for get all archive-files

        :param ids: list of file ids
        :return: response content
        :return: filename
        """
        params = {"ids": ids}
        response = requests.post(self.endpoint, data=json.dumps(params), headers={"Content-Type": "application/json"})
        content = response.content
        header = response.headers["Content-Disposition"]
        output_file = re.findall("filename=(.+)", header)[0]
        return content, output_file
