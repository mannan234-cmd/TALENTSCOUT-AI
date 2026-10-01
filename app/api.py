
from fastapi import FastAPI, HTTPException

from app.models.cv_workflow_api import (
    CVWorkflowRequest,
    CVWorkflowResponse,
)
from app.services.cv_service import CVService
from app.services.cv_workflow_service import CVWorkflowService


app = FastAPI(
    title="TalentScout_AI API",
    version="1.0.0",
    description="API for the TalentScout_AI CV analysis workflow.",
)

workflow_service = CVWorkflowService()
cv_service = CVService()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "TalentScout_AI",
    }


@app.post(
    "/cv/workflow",
    response_model=CVWorkflowResponse,
)
def run_cv_workflow(
    request: CVWorkflowRequest,
) -> CVWorkflowResponse:

    try:

        result = workflow_service.run(
            cv_id=request.cv_id,
            source_text=request.source_text,
            job_description=request.job_description,
        )

        # The workflow persists each AI stage into the CV record.
        # Fetch the record once more so the API can return the
        # persisted structured results to the UI.

        cv_data = cv_service.get_cv(request.cv_id)

        if cv_data is None:
            raise HTTPException(
                status_code=404,
                detail="CV record was not found after workflow execution.",
            )

        return CVWorkflowResponse.from_workflow_result(
            result=result,
            cv_data=cv_data,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"CV workflow execution failed: {type(exc).__name__}: {exc}",
        ) from exc
