import os
import shutil
import pandas as pd
from tqdm import tqdm
import uuid


class Processor:
    def __init__(self, data_path, db):
        self.db = db
        self.data_path = data_path
        self.__arch_dir = "archives/"

    def __get_arch_dir(self):
        return self.__arch_dir + str(uuid.uuid4())

    @staticmethod
    def __extract_file(files, path, name):
        os.system("gzip -d %s" % os.path.join(path, name))
        p = os.path.join(path, name)
        shutil.move(p[:-3], "%s.data_tsv" % path)

        id_ = path.split('/')[-1]
        if id_ not in files:
            raise Exception("not found id=%s in files" % id_)
        file = files[id_]
        file["path_to_file"] = "%s.data_tsv" % path
        files[id_] = file

    def __extract_all_arch(self, root, data):
        for path, subdirs, files in os.walk(root):
            for name in files:
                if name[-3:] != '.gz':
                    continue
                self.__extract_file(data, path, name)

    @staticmethod
    def __to_dict_files(files):
        d = {}
        for f in files:
            # TODO: change to named tuple
            d[f["id"]] = {
                "project_id": f["cases"][0]["project"]["project_id"],
                "case_id": f["cases"][0]["case_id"]
            }
        return d

    def set_to_db(self, files):
        for f in tqdm(files.items(), desc="count files"):
            df = pd.read_csv(f[1]["path_to_file"], sep='\t', header=None)
            df["project_id"] = f[1]["project_id"]
            df["case_id"] = f[1]["case_id"]
            df.columns = ["gene", "expression", "project_id", "case_id"]
            self.db.insert_with_repl(df)

    def run(self, content, files, file_name):
        # TODO: check CheckSum
        files_d = self.__to_dict_files(files)
        with open(self.data_path + file_name, "wb") as output_file:
            output_file.write(content)

        arch_dir = self.__get_arch_dir()

        if os.path.exists(self.data_path + arch_dir):
            shutil.rmtree(self.data_path + arch_dir)
        os.mkdir(self.data_path + arch_dir)
        os.system("tar -xzf %s -C %s" % (self.data_path + file_name, self.data_path + arch_dir))
        self.__extract_all_arch(self.data_path + arch_dir, files_d)
        self.set_to_db(files_d)
        if os.path.exists(self.data_path + arch_dir):
            shutil.rmtree(self.data_path + arch_dir)
        if os.path.exists(self.data_path + file_name):
            os.remove(self.data_path + file_name)
