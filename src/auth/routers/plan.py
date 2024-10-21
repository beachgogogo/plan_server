from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from src.model import TokenData, NewPlanRecv, PlanUID
from src.user_authentication import get_current_user_token
from src.database_method import create_plan_by_doc, str_to_objectid, del_plan
from src.tool.packaging_tool import response_data


plan_router = APIRouter()


@plan_router.post("/plan")
async def api_create_plan(
    token: Annotated[TokenData, Depends(get_current_user_token)],
    plan_info: NewPlanRecv
):
    """
    create a plan
    :param token:
    :param plan_info:
    :return:
    """
    plan_doc = plan_info.model_dump_doc()
    temp_list = []
    for item in plan_doc.task_list:
        temp_list.append(str_to_objectid(item))
    plan_doc.task_list = temp_list
    plan_doc["user_id"] = await get_user_id(token.email)
    ret_json = await create_plan_by_doc(plan_doc)
    response_data(data=ret_json)


@plan_router.delete("/plan")
async def api_delete_plan(
    token: Annotated[TokenData, Depends(get_current_user_token)],
    plan_info: PlanUID
):
    await del_plan(plan_info.plan_id)



