import json
import requests
from copy import deepcopy


class FilesClient:
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
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def get_files(self, ids):
        # TODO: check data in database
        params = {"ids": ids}
        return requests.post(self.endpoint, data=json.dumps(params), headers={"Content-Type": "application/json"})
