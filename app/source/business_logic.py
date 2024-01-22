from  time import sleep

async def process_request(loop_count):
    logger.info('Processing the request...')
    import pandas as pd
    import numpy as np
    df1 = pd.DataFrame(np.random.rand(10000, 10000))
    df3 = df1.mul(df1)
    for index, row in df3.iterrows():
    # Access data using column names
        if index < loop_count:
            pass

    return {"status" : "The Application has Completed Successfully"}