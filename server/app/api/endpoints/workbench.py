from fastapi import APIRouter, Body
from typing import Any
from app.schemas.workbench import (
    ApiResponse, CreateFolderRequest, RenameFolderRequest,
    DeleteFolderRequest, MoveFolderRequest, SyncFolderRequest,
    CreateConfigRequest, RenameConfigRequest, MoveConfigRequest,
    SyncConfigRequest, UpdateConfigTypeRequest,
)
from app.services.workbench_service import (
    get_spaces, get_nodes, build_tree, create_folder, rename_folder,
    delete_folder, move_folder, sync_folder, create_config, rename_config,
    delete_config, move_config, get_config_content, save_config_content,
    update_config_type, sync_config,
)

router = APIRouter(prefix="/workbench", tags=["Workbench"])


@router.get("/api/spaces")
def _get_spaces() -> ApiResponse:
    data = get_spaces()
    return ApiResponse(data=data)


@router.get("/api/spaces/{space_id}/nodes")
def _get_nodes(space_id: str) -> ApiResponse:
    data, error = get_nodes(space_id)
    if error:
        return ApiResponse(code=404, message=error)
    return ApiResponse(data=build_tree(data))


@router.post("/api/spaces/{space_id}/folders")
def _create_folder(space_id: str, req: CreateFolderRequest = Body(...)) -> ApiResponse:
    data, error = create_folder(space_id, req.name, req.parentId)
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
def _rename_folder(space_id: str, req: RenameFolderRequest = Body(...)) -> ApiResponse:
    data, error = rename_folder(space_id, req.id, req.newName)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.delete("/api/spaces/{space_id}/folders/delete")
def _delete_folder(space_id: str, req: DeleteFolderRequest = Body(...)) -> ApiResponse:
    data, error = delete_folder(space_id, req.id)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.patch("/api/spaces/{space_id}/folders/move")
def _move_folder(space_id: str, req: MoveFolderRequest = Body(...)) -> ApiResponse:
    data, error = move_folder(space_id, req.sourceId, req.targetParentId)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.post("/api/spaces/{space_id}/folders/{folder_id}/sync")
def _sync_folder(space_id: str, folder_id: int, req: SyncFolderRequest = Body(...)) -> ApiResponse:
    success, error = sync_folder(space_id, folder_id, req.targetSpaceId)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=None)


@router.post("/api/spaces/{space_id}/configs")
def _create_config(space_id: str, req: CreateConfigRequest = Body(...)) -> ApiResponse:
    data, error = create_config(space_id, req.configId, req.name, req.componentType, req.folderId)
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
def _rename_config(config_id: str, req: RenameConfigRequest = Body(...)) -> ApiResponse:
    data, error = rename_config(config_id, req.newName)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.delete("/api/configs/{config_id}")
def _delete_config(config_id: str) -> ApiResponse:
    data, error = delete_config(config_id)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.patch("/api/configs/{config_id}/move")
def _move_config(config_id: str, req: MoveConfigRequest = Body(...)) -> ApiResponse:
    data, error = move_config(config_id, req.targetFolderId)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.get("/api/configs/{config_id}/content")
def _get_config_content(config_id: str) -> ApiResponse:
    data, error = get_config_content(config_id)
    if error:
        return ApiResponse(code=404, message=error)
    return ApiResponse(data=data)


@router.put("/api/configs/{config_id}/content")
def _save_config_content(config_id: str, content: Any = Body(...)) -> ApiResponse:
    success, error = save_config_content(config_id, content)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=None)


@router.patch("/api/configs/{config_id}/type")
def _update_config_type(config_id: str, req: UpdateConfigTypeRequest = Body(...)) -> ApiResponse:
    data, error = update_config_type(config_id, req.componentType)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        if '只读' in error:
            return ApiResponse(code=403, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=data)


@router.post("/api/preview/mock-data")
def get_preview_mock_data() -> ApiResponse:
    return ApiResponse(data={'list': [], 'total': 0})


@router.post("/api/configs/{config_id}/sync")
def _sync_config(config_id: str, req: SyncConfigRequest = Body(...)) -> ApiResponse:
    success, error = sync_config(config_id, req.targetSpaceId)
    if error:
        if '不存在' in error:
            return ApiResponse(code=404, message=error)
        return ApiResponse(code=400, message=error)
    return ApiResponse(data=None)