from __future__ import annotations

import asyncio
import os
import threading
from abc import ABC, abstractmethod

import websockets

from .driver import DriverClass, DriverFactory, Driver
from .setting import Setting, root


class Barrage(threading.Thread):
    def __init__(self):
        super().__init__()
        self.page: str | None = None
        self.host = "127.0.0.1"
        self.port = 8080
        self.is_login = False
        self.isWss = False
        self.driver: Driver | None = None
        # 收到弹慕的异步回调函数
        self.callback = None
        self.script: str | None = None
        self.element: Element | None = None
        self.event = threading.Event()
        if not self.driver:
            self.driver = DriverFactory.create(DriverClass.CHROME)
        if not self.element:
            self.element = DYElement()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.driver.open(self.page)
        self.event.set()
        wsurl = f"ws://{self.host}:{self.port}"
        if self.isWss:
            wsurl = f"wss://{self.host}/{self.port}"
        self.driver.wait(self.element.sign_css)
        self.driver.inject(self.script, *Setting(wsurl).to_args())
        print(f"服务启动{wsurl}")
        loop.run_until_complete(self._start_websocket_server())
        loop.run_forever()
        print(f"服务关闭{wsurl}")

    async def _start_websocket_server(self):
        # 启动WebSocket服务器
        await websockets.serve(self.__handler, self.host, self.port)


    async def __handler(self, websocket, path):
        # 这个函数将处理WebSocket连接
        async for message in websocket:
            # 处理接收到的消息
            await self.callback(message)

    def send(self, text):
        self.event.wait()
        if not self.is_login:
            print('请先扫码登入')
            self.driver.wait(self.element.login_success_css)
            print("登入成功")
            self.is_login = True
        self.driver.write(self.element.barrage_input_css, text)
        self.driver.click(self.element.send_btn_css)


class Builder(ABC):
    @abstractmethod
    def port(self, port: int):
        pass

    @abstractmethod
    def host(self, host: str):
        pass

    @abstractmethod
    def driver(self, driver: DriverClass):
        pass

    @abstractmethod
    def page(self, url: str):
        pass

    @abstractmethod
    def enableWSS(self):
        pass

    @abstractmethod
    def on(self, callback):
        pass


class Element(ABC):
    def __init__(self):
        self.barrage_input_css = ""
        self.send_btn_css = ""
        self.login_success_css = ""
        self.sign_css = ""


class DYElement(Element):
    def __init__(self):
        super().__init__()
        self.barrage_input_css = ".webcast-chatroom___textarea"
        self.send_btn_css = ".webcast-chatroom___send-btn"
        self.login_success_css = "header a.B3AsdZT9>div.avatar-component-avatar-container>img.PbpHcHqa"
        self.sign_css = ".webcast-chatroom___bottom-message"


class BarrageBuilder(Builder, ABC):
    def __init__(self):
        self.barrage = Barrage()

    def douyin(self):
        self.barrage.element = DYElement()
        self.barrage.script = os.path.join(root, "script/douyin.js")
        return self

    def host(self, host: str):
        self.barrage.host = host
        return self

    def page(self, url: str):
        self.barrage.page = url
        return self

    def port(self, port: int):
        self.barrage.port = port
        return self

    def driver(self, driver: DriverClass):
        self.barrage.driver = DriverFactory.create(driver)
        return self

    def on(self, callback):
        self.barrage.callback = callback
        return self

    def enableWSS(self):
        self.barrage.isWss = True
        return self

    def build(self) -> Barrage:
        return self.barrage
