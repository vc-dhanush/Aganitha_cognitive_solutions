from fastapi import FastAPI

from aganitha_cognitive_solutions import __version__

app = FastAPI(title="Aganitha Cognitive Solutions", version=__version__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}
