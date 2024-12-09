from version.v1.uow import UowV1
from version.v1.logic.telegram.folder_managment import (
    AllManagersFactory,
    DailyFoldersManager,
    FolderStatistics,
    DialogManager,
    FolderUtils,
)
from version.v1.operations.cards import (
    WhiteCardOperation,
    BlackCardOperation,
    ModerateCardNumbersOperation
)
from src.config import client
from src.config.scheduler_singl import SchedulerSingleton
from src.utils import get_name
from src.operations.base import OperationFactory
from version.v1.operations.managers import ManagersOperation, AddManagersOperation
from version.v1.operations.statistic import StatisticOperation, StatisticOperationNew
from version.v1.operations.daily import DailyFoldersOperation
from version.v1.operations.users import RegisterUserOperation
from version.v1.logic.google.google_sheet import GoogleSheet
from version.v1.logic.google import get_creds
from version.v2.tasks.ping import ping


def bootstrap() -> OperationFactory:
    '''
    Bootstrap the application.
    Note:
        - Для регистрации операций используется фабрика операций.
        - Операции обязательный тип BaseOperation.
        - Для регистрации зависимостей используется словарь.
        - При вызове операции, создается экземпляр операции с зависимости.
    Call example:
        bootstrap_['statistic']()
    '''
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
    
    scheduler = SchedulerSingleton()
    operation_factory = OperationFactory()
    
    google_dp = GoogleSheet(generate_creds=get_creds)
    
    operation_factory.register(
        'white_card',
        WhiteCardOperation,
        dependencies={
            'google_dp': google_dp,
            'uow': uow,
            'client': client
        }
    )
    operation_factory.register(
        'black_card',
        BlackCardOperation,
        dependencies={
            'google_dp': google_dp,
            'uow': uow,
            'client': client
        }
    )
    operation_factory.register(
        'managers',
        ManagersOperation,
        dependencies={
            'uow': uow,
            'client': client
        }
    )
    operation_factory.register(
        'add_managers',
        AddManagersOperation,
        dependencies={
            'uow': uow,
            'client': client
        }
    )
    operation_factory.register(
        'statistic',
        StatisticOperation,
        dependencies={
            'all_managers': all_managers,
            'uow': uow,
            'client': client
        }
    )
    operation_factory.register(
        'statistic_new',
        StatisticOperationNew,
        dependencies={
            'all_managers': all_managers,
            'uow': uow,
            'client': client
        }
    )
    operation_factory.register(
        'moderate_card_numbers',
        ModerateCardNumbersOperation,
        dependencies={
            'uow': uow,
            'client': client
        }
    )
    operation_factory.register(
        'register_user',
        RegisterUserOperation,
        dependencies={
            'uow': uow,
            'client': client,
            'all_managers': all_managers,
            'scheduler': scheduler,
            'ping_function': ping,
            'get_name_function': get_name
        }
    )
    operation_factory.register(
        'daily_folders',
        DailyFoldersOperation,
        dependencies={
            'all_managers': all_managers,
            'uow': uow,
            'client': client
        }
    )
    return operation_factory

bootstrap_ = bootstrap()