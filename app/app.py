import os
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Depends, HTTPException

from app.database import init_db
from app.genetic import genetic_algorithm
from app.repository import get_repository, ResourceRepository
from app.requests import ResourceRequest, VMRequest, PredictRequest

app = FastAPI()
app.add_event_handler("startup", init_db)


@app.post("/resource", status_code=201)
async def create(resource: ResourceRequest, repo: ResourceRepository = Depends(get_repository)):
    resource_model = resource.to_model()
    repo.create(resource_model)

    return {
        "id": resource_model.id,
    }


@app.get("/resource")
async def list_resources(repo: ResourceRepository = Depends(get_repository)):
    return repo.retrieve_all()


@app.get("/resource/{resource_id}")
async def retrieve_by_id(resource_id: str, repo: ResourceRepository = Depends(get_repository)):
    resource = repo.retrieve_by_id(resource_id)

    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")

    return resource


@app.put("/resource/{resource_id}")
async def update_resource(
        resource_id: str,
        resource_request: ResourceRequest,
        repo: ResourceRepository = Depends(get_repository)
):
    resource = repo.retrieve_by_id(resource_id)

    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")

    resource_model = resource_request.to_model()
    repo.update(resource_id, resource_model)

    return resource_model


@app.post("/vm/predict")
async def predict_vm(
        req: PredictRequest,
        repo: ResourceRepository = Depends(get_repository),
):
    resources = repo.retrieve_all()
    try:
        solution = genetic_algorithm(
            req,
            resources,
        )

        return solution.to_response()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/plot")
async def get_genetic_plot():
    from fastapi.responses import FileResponse
    file_path = "./plot/fitness_plot.png"

    return FileResponse(path=file_path, media_type='image/png', filename='fitness_plot.png')


@app.get("/plot/infra", response_class=HTMLResponse)
async def list_resource_files():
    directory = "./plot/"
    files = [file for file in os.listdir(directory) if file.startswith("resource_utilization_gen")]

    html_content = "<html><body><h1>Resource Utilization Files</h1><ul>"
    for file in files:
        file_url = f"/plot/infra/{file}"
        html_content += f'<li><a href="{file_url}">{file}</a></li>'
    html_content += "</ul></body></html>"

    return HTMLResponse(content=html_content)


@app.get("/plot/infra/{file_name}", response_class=HTMLResponse)
async def get_resource_file(file_name: str):
    directory = "./plot/"
    if not file_name.startswith("resource_utilization_gen"):
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join(directory, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    files = [file for file in os.listdir(directory) if file.startswith("resource_utilization_gen")]

    html_content = f'<html><body><h1>{file_name}</h1>'
    html_content += "<h2>Resource Utilization Files</h2><ul>"
    for file in files:
        file_url = f"/plot/infra/{file}"
        html_content += f'<li><a href="{file_url}">{file}</a></li>'

    html_content += f'<img src="/plot/{file_name}" alt="{file_name}">'
    html_content += "</ul></body></html>"

    return HTMLResponse(content=html_content)


@app.get("/plot/{file_name}")
async def get_plot_file(file_name: str):
    from fastapi.responses import FileResponse
    directory = "./plot/"
    file_path = os.path.join(directory, file_name)

    if os.path.exists(file_path) and file_name.startswith("resource_utilization_gen"):
        return FileResponse(path=file_path, media_type='image/png', filename=file_name)
    else:
        raise HTTPException(status_code=404, detail="File not found")
