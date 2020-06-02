from datetime import datetime, timedelta, timezone


class Env:
    project_id = "<project-id>"
    bucket_name = project_id

    @classmethod
    def blob_name(cls, run_name):
        return f"code/{run_name}.tar.gz"

    @classmethod
    def blob_name_run_info(cls, run_name):
        return f"run_info/{run_name}.json"
