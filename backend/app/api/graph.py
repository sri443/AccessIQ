from fastapi import APIRouter, HTTPException
from app.api.analysis import ANALYZED_USERS
from app.graph.identity_graph import IdentityGraph
from app.models.schemas import GraphData

router = APIRouter()
identity_graph = IdentityGraph()

@router.get("/")
async def get_graph(user_id: str = None) -> GraphData:
    if not ANALYZED_USERS: raise HTTPException(400, "Please run analysis first")
    if user_id: graph_data = identity_graph.get_user_subgraph(user_id)
    else: graph_data = identity_graph.build_graph(ANALYZED_USERS)
    return GraphData(**graph_data)