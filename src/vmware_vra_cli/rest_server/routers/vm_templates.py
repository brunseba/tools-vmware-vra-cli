"""VM Templates API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from vmware_vra_cli.rest_server.database import get_db_session, VMTemplate
import uuid

router = APIRouter(prefix="/vm-templates", tags=["vm-templates"])


# Pydantic models for request/response
class VMTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    catalogItemId: Optional[str] = None
    catalogItemName: Optional[str] = None
    inputs: dict = {}


class VMTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    catalogItemId: Optional[str] = None
    catalogItemName: Optional[str] = None
    inputs: Optional[dict] = None


class VMTemplateResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    catalogItemId: Optional[str]
    catalogItemName: Optional[str]
    inputs: dict
    createdAt: str
    updatedAt: str


class VMTemplateListResponse(BaseModel):
    success: bool
    message: str
    templates: List[VMTemplateResponse]
    total_count: int


@router.get("", response_model=VMTemplateListResponse)
async def list_templates(
    db: Session = Depends(get_db_session),
    search: Optional[str] = None,
):
    """List all VM templates."""
    try:
        query = db.query(VMTemplate)
        
        # Apply search filter
        if search:
            query = query.filter(
                (VMTemplate.name.ilike(f"%{search}%")) |
                (VMTemplate.description.ilike(f"%{search}%"))
            )
        
        templates = query.order_by(VMTemplate.updated_at.desc()).all()
        
        return VMTemplateListResponse(
            success=True,
            message=f"Found {len(templates)} template(s)",
            templates=[VMTemplateResponse(**t.to_dict()) for t in templates],
            total_count=len(templates),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch templates: {str(e)}")


@router.get("/{template_id}", response_model=VMTemplateResponse)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db_session),
):
    """Get a specific VM template by ID."""
    try:
        template = db.query(VMTemplate).filter(VMTemplate.id == template_id).first()
        
        if not template:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        
        return VMTemplateResponse(**template.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch template: {str(e)}")


@router.post("", response_model=VMTemplateResponse, status_code=201)
async def create_template(
    template_data: VMTemplateCreate,
    db: Session = Depends(get_db_session),
):
    """Create a new VM template."""
    try:
        # Generate unique ID
        template_id = str(uuid.uuid4())
        
        # Create new template
        new_template = VMTemplate(
            id=template_id,
            name=template_data.name,
            description=template_data.description,
            catalog_item_id=template_data.catalogItemId,
            catalog_item_name=template_data.catalogItemName,
            inputs=template_data.inputs,
        )
        
        db.add(new_template)
        db.commit()
        db.refresh(new_template)
        
        return VMTemplateResponse(**new_template.to_dict())
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.put("/{template_id}", response_model=VMTemplateResponse)
async def update_template(
    template_id: str,
    template_data: VMTemplateUpdate,
    db: Session = Depends(get_db_session),
):
    """Update an existing VM template."""
    try:
        template = db.query(VMTemplate).filter(VMTemplate.id == template_id).first()
        
        if not template:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        
        # Update fields if provided
        if template_data.name is not None:
            template.name = template_data.name
        if template_data.description is not None:
            template.description = template_data.description
        if template_data.catalogItemId is not None:
            template.catalog_item_id = template_data.catalogItemId
        if template_data.catalogItemName is not None:
            template.catalog_item_name = template_data.catalogItemName
        if template_data.inputs is not None:
            template.inputs = template_data.inputs
        
        template.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(template)
        
        return VMTemplateResponse(**template.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update template: {str(e)}")


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    db: Session = Depends(get_db_session),
):
    """Delete a VM template."""
    try:
        template = db.query(VMTemplate).filter(VMTemplate.id == template_id).first()
        
        if not template:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        
        db.delete(template)
        db.commit()
        
        return {
            "success": True,
            "message": f"Template {template.name} deleted successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {str(e)}")
