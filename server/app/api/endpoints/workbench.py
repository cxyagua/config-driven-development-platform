from fastapi import APIRouter, Body, Depends
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.workbench import (
    ApiResponse, CreateFolderRequest, RenameFolderRequest,
    DeleteFolderRequest, MoveFolderRequest, SyncFolderRequest,
    CreateConfigRequest, RenameConfigRequest, MoveConfigRequest,
    SyncConfigRequest, UpdateConfigTypeRequest,
)
from app.services.workbench_service_db import (
    get_spaces, get_nodes, build_tree, create_folder, rename_folder,
    delete_folder, move_folder, sync_folder, create_config, rename_config,
    delete_config, move_config, get_config_content, save_config_content,
    update_config_type, sync_config,
)

router = APIRouter(prefix="/workbench", tags=["Workbench"])


@router.get("/api/spaces")
async def _get_spaces(db: AsyncSession = Depends(get_db)) -> ApiResponse:
    data = await get_spaces(db)
    return ApiResponse(data=data)


@router.get("/api/spaces/{space_id}/nodes")
async def _get_nodes(space_id: str, db: AsyncSession = Depends(get_db)) -> ApiResponse:
    data, error = await get_nodes(db, space_id)
    if error:
        return ApiResponse(code=404, message=error)
    return ApiResponse(data=build_tree(data))


@router.post("/api/spaces/{space_id}/folders")
async def _create_folder(space_id: str, req: CreateFolderRequest = Body(...), db: AsyncSession = Depends(get_db)) -> ApiResponse:
    data, error = await create_folder(db, space_id, req.name, req.parentId)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        if '已存在' in error:
            return ApiResponse(code=409, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.patch("/api/spaces/{space_id}/folders/rename")
async def _rename_folder(space_id: str, req: RenameFolderRequest = Body(...), db: AsyncSession = Depends(get_db)) -> ApiResponse:
    data, error = await rename_folder(db, space_id, req.id, req.newName)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.delete("/api/spaces/{space_id}/folders/delete")
async def _delete_folder(space_id: str, req: DeleteFolderRequest = Body(...), db: AsyncSession = Depends(get_db)) -> ApiResponse:
    data, error = await delete_folder(db, space_id, req.id)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.patch("/api/spaces/{space_id}/folders/move")
async def _move_folder(space_id: str, req: MoveFolderRequest = Body(...), db: AsyncSession = Depends(get_db)) -> ApiResponse:
    data, error = await move_folder(db, space_id, req.sourceId, req.targetParentId)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.post("/api/spaces/{space_id}/folders/{folder_id}/sync")
async def _sync_folder(space_id: str, folder_id: int, req: SyncFolderRequest = Body(...), db: AsyncSession = Depends(get_db)) -> ApiResponse:
    success, error = await sync_folder(db, space_id, folder_id, req.targetSpaceId)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=None)


@router.post("/api/spaces/{space_id}/configs")
async def _create_config(space_id: str, req: CreateConfigRequest = Body(...), db: AsyncSession = Depends(get_db)) -> ApiResponse:
    data, error = await create_config(db, space_id, req.configId, req.name, req.componentType, req.folderId)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        if '已存在' in error:
            return ApiResponse(code=409, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.patch("/api/configs/{config_id}/rename")
async def _rename_config(config_id: str, req: RenameConfigRequest = Body(...), db: AsyncSession = Depends(get_db)) -> ApiResponse:
    data, error = await rename_config(db, config_id, req.newName)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.delete("/api/configs/{config_id}")
async def _delete_config(config_id: str, db: AsyncSession = Depends(get_db)) -> ApiResponse:
    data, error = await delete_config(db, config_id)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.patch("/api/configs/{config_id}/move")
async def _move_config(config_id: str, req: MoveConfigRequest = Body(...), db: AsyncSession = Depends(get_db)) -> ApiResponse:
    data, error = await move_config(db, config_id, req.targetFolderId)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.get("/api/configs/{config_id}/content")
async def _get_config_content(config_id: str, db: AsyncSession = Depends(get_db)) -> ApiResponse:
    data, error = await get_config_content(db, config_id)
    if error:
        return ApiResponse(code=404, message=error)
    return ApiResponse(data=data)


@router.put("/api/configs/{config_id}/content")
async def _save_config_content(config_id: str, content: Any = Body(...), db: AsyncSession = Depends(get_db)) -> ApiResponse:
    success, error = await save_config_content(db, config_id, content)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=None)


@router.patch("/api/configs/{config_id}/type")
async def _update_config_type(config_id: str, req: UpdateConfigTypeRequest = Body(...), db: AsyncSession = Depends(get_db)) -> ApiResponse:
    data, error = await update_config_type(db, config_id, req.componentType)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.post("/api/preview/mock-data")
async def get_preview_mock_data() -> ApiResponse:
    return ApiResponse(data={'list': [], 'total': 0})


@router.post("/api/configs/{config_id}/sync")
async def _sync_config(config_id: str, req: SyncConfigRequest = Body(...), db: AsyncSession = Depends(get_db)) -> ApiResponse:
    success, error = await sync_config(db, config_id, req.targetSpaceId)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=None)