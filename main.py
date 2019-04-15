import re
import json
import argparse

from flask import Flask, request, logging

from client.db import SQLiteClient
from client.gdc import FilesClient, DataClient
from processor.archives import Processor
from draw.hist import build_hist

# TODO: add swagger
# TODO: may be add lru


def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, help="path to config")
    parser.add_argument("--hard", type=str, help="reset data base", default=False)
    return parser.parse_args()


args = arg_parse()
config_path = args.config
is_hard = args.hard

with open(config_path) as fd:
    config = json.load(fd)

app = Flask(config["service"])
logger = logging.create_logger(app)
logger.setLevel(20)

# TODO: change path to connector
dbClient = SQLiteClient(config["db_path"])
files_client = FilesClient(
    config["files"]["batch_size"],
    config["files"]["filters"],
    config["files"]["fields"],
    config["files"]["endpoint"]
)
data_client = DataClient(config["data"]["endpoint"])
arch_processor = Processor(config["data"]["path"], dbClient)


# example: http://127.0.0.1:5000/download?project_id=TCGA-PCPG&count=80
@app.route('/download', methods=['GET'])
def download():
    project_id = request.args.get("project_id")
    if project_id is None:
        return "bad request", 400
    count = request.args.get("count")
    if count is not None and count.isdigit() and int(count) <= 1:
        return "count parameter must be > 1", 400
    app.logger.info("request to gdc api (files)")
    try:
        files = files_client.get_files(project_id)
    except Exception as e:
        app.logger.error("gdc api error (data) (error='%s')" % str(e))
        return "internal server error", 500

    ids = [fId['id'] for fId in files]
    if count is not None and count.isdigit():
        ids = ids[:int(count)]
        files = files[:int(count)]
    app.logger.info("request to gdc api (data)")
    # TODO: check data in database
    try:
        response = data_client.get_files(ids)
    except Exception as e:
        app.logger.error("gdc api (data) error (error='%s')" % str(e))
        return "internal server error", 500

    app.logger.info("extracting data")
    try:
        content = response.content
        header = response.headers["Content-Disposition"]
        output_file = re.findall("filename=(.+)", header)[0]
        arch_processor.run(content, files, output_file)
    except Exception as e:
        app.logger.error("processor error (error='%s')" % str(e))
        return "internal server error", 500

    return "files got: %s" % str(ids), 200


# example: http://127.0.0.1:5000/distribution?gene_id=ENSG00000167578.15&project_id=TCGA-PCPG&bins=20
@app.route('/distribution')
def distribution():
    project_id = request.args.get("project_id")
    if project_id is None:
        return "bad request", 400
    gene_id = request.args.get("gene_id")
    if gene_id is None:
        return "bad request", 400
    bins = request.args.get("bins")
    if bins is not None and bins.isdigit():
        # TODO: move value to config
        bins = int(bins)
    else:
        bins = 10
    res = dbClient.select_genes(gene_id, project_id)
    return build_hist(res, bins)


if __name__ == "__main__":
    app.run()
