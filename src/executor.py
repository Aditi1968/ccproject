# src/executor.py

import subprocess, uuid, os, shutil, logging, time
from .metrics import log_metric

logging.basicConfig(level=logging.INFO)

def execute_with_runtime(code: str, timeout: int = 5, runtime: str = "docker") -> str:
    run_id = str(uuid.uuid4())
    temp_dir = f"/tmp/{run_id}"
    os.makedirs(temp_dir)

    image_tag = f"temp-func-{run_id}"
    start = time.time()

    try:
        # Write the function code
        func_path = os.path.join(temp_dir, "function.py")
        with open(func_path, "w") as f:
            f.write(code)

        # Copy base Dockerfile
        shutil.copy("docker_images/python/Dockerfile", os.path.join(temp_dir, "Dockerfile"))

        # Build the image
        subprocess.run(["docker", "build", "-t", image_tag, "."], cwd=temp_dir, check=True)

        # Select runtime command
        if runtime == "gvisor":
            cmd = ["docker", "run", "--rm", "--runtime=runsc", image_tag]
        else:
            cmd = ["docker", "run", "--rm", image_tag]

        # Run the container
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        success = result.returncode == 0
        output = result.stdout if success else result.stderr

    except subprocess.TimeoutExpired:
        output = "❌ Error: Function timed out."
        success = False

    except Exception as e:
        output = f"❌ Error: {str(e)}"
        success = False

    finally:
        duration = time.time() - start
        log_metric(code, runtime, duration, success)
        subprocess.run(["docker", "rmi", "-f", image_tag])
        shutil.rmtree(temp_dir, ignore_errors=True)

    return output


def execute_python_function(code: str, timeout: int = 5) -> str:
    run_id = str(uuid.uuid4())
    temp_dir = f"/tmp/{run_id}"
    os.makedirs(temp_dir)

    try:
        func_path = os.path.join(temp_dir, "function.py")
        with open(func_path, "w") as f:
            f.write(code)

        shutil.copy("docker_images/python/Dockerfile", os.path.join(temp_dir, "Dockerfile"))

        image_tag = f"function-{run_id}"
        logging.info(f"Building Docker image {image_tag}...")

        subprocess.run(["docker", "build", "-t", image_tag, "."], cwd=temp_dir, check=True)

        logging.info(f"Running container {image_tag}...")

        result = subprocess.run(
            ["docker", "run", "--rm", image_tag],
            capture_output=True, text=True, timeout=timeout
        )

        logging.info("Execution complete.")
        return result.stdout if result.returncode == 0 else result.stderr

    except subprocess.TimeoutExpired:
        return "❌ Error: Function timed out."

    except Exception as e:
        return f"❌ Error: {str(e)}"

    finally:
        logging.info("Cleaning up...")
        subprocess.run(["docker", "rmi", "-f", image_tag])
        shutil.rmtree(temp_dir, ignore_errors=True)


def warm_up_container():
    subprocess.run(["docker", "pull", "python:3.9-slim"])
    logging.info("Warm-up complete: Base image pulled.")


def precreate_pool(tag="base-python", count=3):
    dockerfile_path = os.path.abspath("docker_images/python/Dockerfile")
    context_path = os.path.abspath(".")

    # Ensure dummy file exists
    dummy_code = "print('This is a base container warm-up')"
    with open("function.py", "w") as f:
        f.write(dummy_code)

    for i in range(count):
        subprocess.run(
            ["docker", "build", "-t", f"{tag}-{i}", "-f", dockerfile_path, context_path],
            check=True
        )
        logging.info(f"Container image {tag}-{i} ready.")

    # Clean up dummy file after building
    os.remove("function.py")
