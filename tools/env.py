from datetime import datetime, timedelta, timezone
import random, string


class Env:
    project_id = "<project-id>"
    docker_file_base = "docker/dockerfile-base-anaconda"
    docker_file = "docker/dockerfile-anaconda"
    image_base_name = "cpu-202005-anaconda"
    image_name = project_id + "-anaconda"
    gcr_path = f"gcr.io/{project_id}/{image_name}"
    local_target_dir = "code"
    bucket_name = project_id
    zone = "us-central1-c"
    region = "us-central1"
    cloud_task_queue = 'judge-queue'
    service_name = "judge-service"
    cloud_run_root_url = "<cloud_run_root_url>"
    cloud_run_url = f"{cloud_run_root_url}/run"
    cloud_run_invoker_email = f"invoker-service-account@{project_id}.iam.gserviceaccount.com"

    @classmethod
    def generate_run_name(cls):
        jst = timezone(timedelta(hours=+9), 'jst')
        jst_datetime = datetime.now(jst)
        format_str = '%Y%m%d%H%M%S'
        date_str = jst_datetime.strftime(format_str)

        rand_chars = [random.choice(string.ascii_lowercase) for i in range(3)]
        rand_str = "".join(rand_chars)

        return f"gcp-{date_str}-{rand_str}"

    @classmethod
    def blob_name(cls, run_name):
        return f"code/{run_name}.tar.gz"

    @classmethod
    def blob_name_run_info(cls, run_name):
        return f"run_info/{run_name}.json"
