# HfSI Project
## Build
```bash
docker compose build
```
<details>

<summary>output</summary>

```
[+] Building 3.2s (12/12) FINISHED                                       docker:desktop-linux
 => [hfsi internal] load build definition from Dockerfile                                0.0s
 => => transferring dockerfile: 789B                                                     0.0s
 => [hfsi internal] load metadata for docker.io/library/python:3.9-slim                  0.8s
 => [hfsi internal] load .dockerignore                                                   0.0s
 => => transferring context: 2B                                                          0.0s
 => [hfsi 1/6] FROM docker.io/library/python:3.9-slim@sha256:6250eb7983c08b3cf5a7db9309  0.0s
 => [hfsi internal] load build context                                                   0.4s
 => => transferring context: 4.59MB                                                      0.4s
 => CACHED [hfsi 2/6] WORKDIR /app                                                       0.0s
 => CACHED [hfsi 3/6] RUN apt-get update &&  apt-get install -y  build-essential  curl   0.0s
 => CACHED [hfsi 4/6] COPY requirements.txt /app/                                        0.0s
 => CACHED [hfsi 5/6] RUN pip install --no-cache-dir -r requirements.txt                 0.0s
 => [hfsi 6/6] COPY . /app/                                                              1.3s
 => [hfsi] exporting to image                                                            0.6s
 => => exporting layers                                                                  0.6s
 => => writing image sha256:e1897cb9d209895740c70ac64cc363fce5d517a06fc2fe74460c05f197b  0.0s
 => => naming to docker.io/library/hfsi-hfsi                                             0.0s
 => [hfsi] resolving provenance for metadata file                                        0.0s
```
</details>

## Help
```bash
docker compose run hfsi python3 /app/src/comparison.py --help
```
<details>
<summary>output</summary>

```
usage: comparison.py [-h] -b BASE_DOCUMENT -s SUPPLEMENTAL [SUPPLEMENTAL ...]

Building Code Additions

optional arguments:
  -h, --help            show this help message and exit
  -b BASE_DOCUMENT, --base-document BASE_DOCUMENT
                        Base building code document, e.g. 2022 CA Plumbing Code
  -s SUPPLEMENTAL [SUPPLEMENTAL ...], --supplemental SUPPLEMENTAL [SUPPLEMENTAL ...]
                        Supplemental building code documents, e.g. 2022 SF Plumbing
```

</details>

## Run
Build and run container with base doc and two supplemental docs
```bash
docker compose run --build hfsi python3 /app/src/comparison.py \
  -b /app/src/california_plumbing_code.pdf \
  -s /app/src/oakland_building_code.pdf /app/src/sf_building_code.pdf
```

<details>
<summary>output</summary>

```
[+] Building 3.1s (12/12) FINISHED                                       docker:desktop-linux
 => [hfsi internal] load build definition from Dockerfile                                0.0s
 => => transferring dockerfile: 789B                                                     0.0s
 => [hfsi internal] load metadata for docker.io/library/python:3.9-slim                  0.7s
 => [hfsi internal] load .dockerignore                                                   0.0s
 => => transferring context: 2B                                                          0.0s
 => [hfsi 1/6] FROM docker.io/library/python:3.9-slim@sha256:6250eb7983c08b3cf5a7db9309  0.0s
 => [hfsi internal] load build context                                                   0.4s
 => => transferring context: 2.25MB                                                      0.4s
 => CACHED [hfsi 2/6] WORKDIR /app                                                       0.0s
 => CACHED [hfsi 3/6] RUN apt-get update &&  apt-get install -y  build-essential  curl   0.0s
 => CACHED [hfsi 4/6] COPY requirements.txt /app/                                        0.0s
 => CACHED [hfsi 5/6] RUN pip install --no-cache-dir -r requirements.txt                 0.0s
 => [hfsi 6/6] COPY . /app/                                                              1.3s
 => [hfsi] exporting to image                                                            0.6s
 => => exporting layers                                                                  0.6s
 => => writing image sha256:62625a22e1488ea75ae71c15b3e9867ecc3bd3085b88ccde192fba563cf  0.0s
 => => naming to docker.io/library/hfsi-hfsi                                             0.0s
 => [hfsi] resolving provenance for metadata file                                        0.0s
INFO:__main__:Parsing State building code from /app/src/california_plumbing_code.pdf
INFO:__main__:Parsing City 0 building code from /app/src/oakland_building_code.pdf
INFO:__main__:Parsing City 1 building code from /app/src/sf_building_code.pdf
```

</details>
