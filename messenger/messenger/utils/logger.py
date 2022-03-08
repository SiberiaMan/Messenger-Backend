import datetime


async def write_log(message: str):
    with open('log.txt', 'a+') as fd:
        fd.writelines(message)
    print(message.strip())


def logger(func):
    async def inner(*args, **kwargs):
        with open('log.txt', 'a+') as fd:
            fd.write(f'[{datetime.datetime.now()}] -> start function [{func.__name__}]\n')
        print(f'[{datetime.datetime.now()}] -> start function [{func.__name__}]')
        body = await func(*args, **kwargs)
        with open('log.txt', 'a+') as fd:
            fd.write(f'[{datetime.datetime.now()}] -> end function [{func.__name__}]\n\n')
        print(f'[{datetime.datetime.now()}] -> end function [{func.__name__}]')
        return body
    return inner
