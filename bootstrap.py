from version.v1.uow import UowV1
from version.v1.logic.telegram.folder_managment import (
    AllManagersFactory,
    DailyFoldersManager,
    FolderStatistics,
    DialogManager,
    FolderUtils,
)
from version.v1.operations.cards import WhiteCardOperation, BlackCardOperation
from version.v1.operations.managers import ManagersOperation, AddManagersOperation
from version.v1.logic.google.google_sheet import GoogleSheet
from version.v1.logic.google import get_creds


from src.config import client

def bootstrap() -> dict[str, object]:
    uow = UowV1()
    dependencies = {
        "uow": uow,
        "client": client,
    }
    all_managers = AllManagersFactory(
        daily=DailyFoldersManager,
        stats=FolderStatistics,
        dialog=DialogManager,
        utils=FolderUtils,
        dependencies=dependencies
    )
    
    # TODO: Добавить Operations layer
    google_dp = GoogleSheet(generate_creds=get_creds)
    card_operation = WhiteCardOperation(google_dp=google_dp, uow=uow, client=client)
    black_card_operation = BlackCardOperation(google_dp=google_dp, uow=uow, client=client)
    managers_operation = ManagersOperation(uow=uow, client=client)
    add_managers_operation = AddManagersOperation(uow=uow, client=client)
    
    return {
        "all_managers": all_managers,
        "white_card": card_operation,
        "black_card": black_card_operation,
        "managers": managers_operation,
        "add_managers": add_managers_operation,
    }
