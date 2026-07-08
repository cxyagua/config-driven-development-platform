from typing import Any, List, Optional, Union
from pydantic import BaseModel, Field


class SpaceItem(BaseModel):
    id: str
    name: str
    readonly: Optional[bool] = False


class Node(BaseModel):
    nodeType: str = Field(..., description="folder | config")
    name: str
    id: Optional[int] = None
    parentId: Optional[int] = 0
    children: Optional[List["Node"]] = None
    configId: Optional[str] = None
    componentType: Optional[str] = None
    updatedAt: Optional[str] = None
    createdBy: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}


Node.model_rebuild()


class CreateFolderRequest(BaseModel):
    name: str
    parentId: Optional[int] = 0


class RenameFolderRequest(BaseModel):
    id: int
    newName: str


class DeleteFolderRequest(BaseModel):
    id: int


class MoveFolderRequest(BaseModel):
    sourceId: int
    targetParentId: Optional[int] = 0


class SyncFolderRequest(BaseModel):
    targetSpaceId: str


class CreateConfigRequest(BaseModel):
    configId: str
    name: str
    componentType: Optional[str] = "others"
    folderId: Optional[int] = 0


class RenameConfigRequest(BaseModel):
    newName: str


class MoveConfigRequest(BaseModel):
    targetFolderId: int


class SyncConfigRequest(BaseModel):
    targetSpaceId: str


class UpdateConfigTypeRequest(BaseModel):
    componentType: str


class ConfigHistoryItem(BaseModel):
    id: int
    configId: str
    content: Any
    version: int
    createdAt: Optional[str] = None


class RollbackConfigRequest(BaseModel):
    version: int


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: Optional[Any] = None