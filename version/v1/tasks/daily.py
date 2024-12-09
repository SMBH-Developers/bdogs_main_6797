from bootstrap import bootstrap_

async def send_folders_statistic():
    await bootstrap_["statistic"]()

async def send_folders_statistic_new():
    await bootstrap_["statistic_new"]()
    
async def dispatch_users_via_daily_folders():
    await bootstrap_["daily_folders"]()