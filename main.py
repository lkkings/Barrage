from barrage import BarrageBuilder


async def callback(message: str):
    print(message)


if __name__ == '__main__':
    url = "https://live.douyin.com/100844728303"
    barrage = BarrageBuilder().douyin()\
        .page(url)\
        .port(8080)\
        .on(callback)\
        .build()

    barrage.daemon = True
    barrage.start()
    barrage.send("弹慕连接成功")
    barrage.join()
